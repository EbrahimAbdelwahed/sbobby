import nextVitals from 'eslint-config-next/core-web-vitals';

const config = [...nextVitals, { ignores: ['public/ffmpeg/**', '.next/**'] }];

export default config;
