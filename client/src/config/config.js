const devApiBase = "http://127.0.0.1:5000";
const prodApiBase = import.meta.env.VITE_API_BASE || devApiBase;

const config = {
  development: {
    apiBase: devApiBase,
    endpoints: {
      generateOutfit: `${devApiBase}/api/outfit/generate`,
      tryOn: `${devApiBase}/api/tryon`,
      recommendations: `${devApiBase}/api/recommendations`,
      train: `${devApiBase}/api/recommendations/train`,
    },
  },
  production: {
    apiBase: prodApiBase,
    endpoints: {
      generateOutfit: `${prodApiBase}/api/outfit/generate`,
      tryOn: `${prodApiBase}/api/tryon`,
      recommendations: `${prodApiBase}/api/recommendations`,
      train: `${prodApiBase}/api/recommendations/train`,
    },
  },
};

export default config;
