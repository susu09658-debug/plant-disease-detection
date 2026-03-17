<template>
  <div class="index-page">
    <el-card class="welcome-card" shadow="never">
      <h2>欢迎进入植物病害智能检测系统</h2>
      <p>登录成功，当前页面为系统首页占位页。</p>
    </el-card>
  </div>
</template>

<script setup>
</script>

<style scoped>
.index-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f8fc;
}

.welcome-card {
  width: min(680px, 92vw);
  border-radius: 12px;
}

h2 {
  margin: 0 0 8px;
  color: #123b73;
}

p {
  margin: 0;
  color: #5a6a85;
}
</style>
