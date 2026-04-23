import http from 'k6/http';
import { check, sleep } from 'k6';

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8080';
const SPIKE_BASE_VUS = Number(__ENV.SPIKE_BASE_VUS || 5);
const SPIKE_PEAK_VUS = Number(__ENV.SPIKE_PEAK_VUS || 80);

export const options = {
  stages: [
    { duration: '10s', target: SPIKE_BASE_VUS },
    { duration: '5s', target: SPIKE_PEAK_VUS },
    { duration: '20s', target: SPIKE_PEAK_VUS },
    { duration: '10s', target: SPIKE_BASE_VUS },
    { duration: '10s', target: 0 },
  ],
};

export default function () {
  const res = http.get(`${BASE_URL}/products`);

  check(res, {
    'status is 200': (r) => r.status === 200,
    'body is array': (r) => {
      try {
        return Array.isArray(r.json());
      } catch (e) {
        return false;
      }
    },
  });

  sleep(1);
}
