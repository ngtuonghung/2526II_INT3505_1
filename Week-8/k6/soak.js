import http from 'k6/http';
import { check, sleep } from 'k6';

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8080';
const SOAK_VUS = Number(__ENV.SOAK_VUS || 10);

export const options = {
  stages: [
    { duration: '20s', target: SOAK_VUS },
    { duration: '2m', target: SOAK_VUS },
    { duration: '20s', target: 0 },
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
