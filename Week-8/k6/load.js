import http from 'k6/http';
import { check, sleep } from 'k6';

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8080';
const LOAD_VUS = Number(__ENV.LOAD_VUS || 20);

export const options = {
  stages: [
    { duration: '15s', target: LOAD_VUS },
    { duration: '30s', target: LOAD_VUS },
    { duration: '15s', target: 0 },
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
