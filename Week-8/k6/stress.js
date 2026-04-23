import http from 'k6/http';
import { check, sleep } from 'k6';

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8080';
const STRESS_VUS_1 = Number(__ENV.STRESS_VUS_1 || 20);
const STRESS_VUS_2 = Number(__ENV.STRESS_VUS_2 || 40);
const STRESS_VUS_3 = Number(__ENV.STRESS_VUS_3 || 80);

export const options = {
  stages: [
    { duration: '20s', target: STRESS_VUS_1 },
    { duration: '20s', target: STRESS_VUS_2 },
    { duration: '20s', target: STRESS_VUS_3 },
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
