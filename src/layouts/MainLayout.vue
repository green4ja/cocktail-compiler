<template>
  <q-layout view="lHh Lpr lFf">
    <q-page-container>
      <div class="main-content">
        <NavigationBox style="margin-bottom: 20px;"/>
        <router-view />
      </div>
    </q-page-container>
  </q-layout>
</template>

<script setup>
import NavigationBox from 'components/NavigationBox.vue'
</script>

<style scoped>
.main-content {
  padding: 20px;
  height: 100vh;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
}
</style>
