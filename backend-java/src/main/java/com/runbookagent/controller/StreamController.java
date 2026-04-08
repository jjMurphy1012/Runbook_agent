package com.runbookagent.controller;

import java.io.IOException;
import java.util.Map;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

@RestController
@RequestMapping("/api/stream")
public class StreamController {

    private final StringRedisTemplate redisTemplate;

    public StreamController(StringRedisTemplate redisTemplate) {
        this.redisTemplate = redisTemplate;
    }

    @GetMapping(value = "/{alertId}", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public SseEmitter streamAlertEvents(@PathVariable String alertId) {
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
