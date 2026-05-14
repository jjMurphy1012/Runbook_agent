package com.runbookagent.controller;

import com.runbookagent.util.JwtUtil;
import java.io.IOException;
import java.util.Map;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

@RestController
@RequestMapping("/api/stream")
public class StreamController {

    private final StringRedisTemplate redisTemplate;
    private final JwtUtil jwtUtil;

    public StreamController(StringRedisTemplate redisTemplate, JwtUtil jwtUtil) {
        this.redisTemplate = redisTemplate;
        this.jwtUtil = jwtUtil;
    }

    @PostMapping("/token/{alertId}")
    public ResponseEntity<Map<String, String>> issueStreamToken(@PathVariable String alertId) {
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        if (auth == null || !auth.isAuthenticated() || "anonymousUser".equals(auth.getPrincipal())) {
            throw new AccessDeniedException("authentication required");
        }
        String token = jwtUtil.generateStreamToken(auth.getName(), alertId);
        return ResponseEntity.ok(Map.of("token", token));
    }

    @GetMapping(value = "/{alertId}", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public SseEmitter streamAlertEvents(
            @PathVariable String alertId,
            @RequestParam("token") String token) {
        if (!jwtUtil.isValidStreamToken(token, alertId)) {
            throw new AccessDeniedException("invalid or expired stream token");
        }
        SseEmitter emitter = new SseEmitter(120000L);
        String streamKey = "alerts:" + alertId + ":events";

        Thread thread = new Thread(() -> {
            String lastId = "0-0";
            int idleCount = 0;

            try {
                while (idleCount < 120) {
                    var records = redisTemplate.opsForStream()
                            .read(org.springframework.data.redis.connection.stream.StreamOffset.create(
                                    streamKey,
                                    org.springframework.data.redis.connection.stream.ReadOffset.from(lastId)
                            ));

                    if (records != null && !records.isEmpty()) {
                        idleCount = 0;
                        for (var record : records) {
                            lastId = record.getId().getValue();
                            Map<Object, Object> fields = record.getValue();
                            String stage = String.valueOf(fields.getOrDefault("stage", ""));
                            String data = String.valueOf(fields.getOrDefault("data", "{}"));

                            emitter.send(SseEmitter.event()
                                    .name(stage)
                                    .data(data));

                            if ("complete".equals(stage)) {
                                emitter.complete();
                                return;
                            }
                        }
                    } else {
                        idleCount++;
                        Thread.sleep(1000);
                    }
                }
                emitter.complete();
            } catch (IOException | InterruptedException e) {
                emitter.completeWithError(e);
            }
        });
        thread.setDaemon(true);
        thread.start();

        return emitter;
    }

    @GetMapping("/health")
    public Map<String, String> health() {
        return Map.of("service", "stream", "status", "ok");
    }
}
