const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true,
  filenameHashing: true,
  publicPath: process.env.NODE_ENV === 'production' ? '/GenAI-Tutor-Bootcamp-2025-team-5/' : '/'
})
