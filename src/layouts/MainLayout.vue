<template>
  <q-layout view="lHh Lpr lFf">
    <q-page-container>
      <div class="main-content">
        <NavigationBox/>
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
}
</style>
