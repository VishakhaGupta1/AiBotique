const devApiBase = "http://172.16.46.150:5000";
const prodApiBase = import.meta.env.VITE_API_BASE || devApiBase;

const config = {
  development: {
    apiBase: devApiBase,
    endpoints: {
      generateOutfit: `${devApiBase}/api/outfit/generate`,
      recommendations: `${devApiBase}/api/recommendations`,
      train: `${devApiBase}/api/recommendations/train`,
    },
  },
  production: {
    apiBase: prodApiBase,
    endpoints: {
      generateOutfit: `${prodApiBase}/api/outfit/generate`,
      recommendations: `${prodApiBase}/api/recommendations`,
      train: `${prodApiBase}/api/recommendations/train`,
    },
  },
};

export default config;
