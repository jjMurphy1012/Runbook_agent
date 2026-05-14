package com.runbookagent.util;

import static org.junit.jupiter.api.Assertions.assertEquals;

import java.util.LinkedHashMap;
import java.util.Map;
import org.junit.jupiter.api.Test;

/**
 * Fingerprint parity test.
 *
 * Expected hashes are produced by backend-python/agents/fingerprint.py on the
 * same inputs. Any drift between the two implementations fails here.
 */
class FingerprintUtilParityTest {

    @Test
    void matchesPythonForKnownInputs() {
        assertEquals(
                "4cf93c03078a33f24ebd3599eb10676f",
                FingerprintUtil.compute("mysql_pool_exhausted", Map.of())
        );

        Map<String, String> labels1 = new LinkedHashMap<>();
        labels1.put("service", "payment-api");
        labels1.put("host", "db-01");
        assertEquals(
                "d596a9b8951d249f6a59167d61135183",
                FingerprintUtil.compute("mysql_pool_exhausted", labels1)
        );

        Map<String, String> labels2 = new LinkedHashMap<>();
        labels2.put("host", "worker-03");
        labels2.put("zone", "us-west-2a");
        assertEquals(
                "b57b5a2a618191ae176940ed05887869",
                FingerprintUtil.compute("cpu_high_load", labels2)
        );

        assertEquals(
                "66b4a7abb122d8544f7e80257bcfa63f",
                FingerprintUtil.compute("", Map.of())
        );
    }

    @Test
    void isOrderIndependent() {
        Map<String, String> forward = new LinkedHashMap<>();
        forward.put("a", "1");
        forward.put("b", "2");
        Map<String, String> reverse = new LinkedHashMap<>();
        reverse.put("b", "2");
        reverse.put("a", "1");
        assertEquals(
                FingerprintUtil.compute("rule", forward),
                FingerprintUtil.compute("rule", reverse)
        );
        assertEquals(
                "2108536dfbe6668c45f16a6ee756526f",
                FingerprintUtil.compute("rule", forward)
        );
    }

    @Test
    void handlesNullsAsEmpty() {
        assertEquals(
                FingerprintUtil.compute("", Map.of()),
                FingerprintUtil.compute(null, null)
        );
    }
}
