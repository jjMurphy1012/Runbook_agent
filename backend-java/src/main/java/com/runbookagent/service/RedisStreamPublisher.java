package com.runbookagent.service;

import java.util.Map;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;

@Service
public class RedisStreamPublisher {

    private final StringRedisTemplate redisTemplate;

    public RedisStreamPublisher(StringRedisTemplate redisTemplate) {
        this.redisTemplate = redisTemplate;
    }

    public void publishAlertCreated(String alertId) {
        String streamKey = "alerts:" + alertId + ":events";
        Map<String, String> fields = Map.of(
                "stage", "alert_created",
                "data", "{\"alert_id\":\"" + alertId + "\"}"
        );
        redisTemplate.opsForStream().add(streamKey, fields);
    }

    public void publishEvent(String alertId, String stage, String data) {
        String streamKey = "alerts:" + alertId + ":events";
        Map<String, String> fields = Map.of(
                "stage", stage,
                "data", data
        );
        redisTemplate.opsForStream().add(streamKey, fields);
    }
}
