const config = {
  PORT: process.env.HOST_PORT || 3000,
  MINIO_HOST: process.env.MINIO_HOST || 'minio-service',
  MINIO_PORT: parseInt(process.env.MINIO_PORT, 10) || 9000,
  MINIO_ACCESS_KEY: process.env.MINIO_ACCESS_KEY || 'minio',
  MINIO_SECRET_KEY: process.env.MINIO_SECRET_KEY || 'minio123',
  MINIO_BUCKET: process.env.MINIO_BUCKET || 'mlpipeline',
  MINIO_UPLOAD_FOLDER_NAME: process.env.MINIO_UPLOAD_FOLDER_NAME || 'components',
};

export default config;
