<template>
  <div class="buttons-box">
    <div class="function-options">
      <q-btn color="github-seven" text-color="github-zero" label="Make Cocktail" icon="local_bar" class="full-width"></q-btn>
      <q-btn color="github-seven" text-color="github-zero" label="Clean Tubes" icon="wash" class="full-width"></q-btn>
      <q-btn color="github-seven" text-color="github-zero" label="Calibrate Pumps" icon="handyman" class="full-width"></q-btn>
    </div>
  </div>
</template>

<script></script>

<style scoped>
.buttons-box {
  width: 100%;
  flex: 1;
  box-sizing: border-box;
  outline: 2px solid #b1bac4;
  padding: 20px;
  background-color: #30363d;
  display: flex;
  flex-direction: column;
}

.function-options {
  display: flex;
  flex-direction: column;
  gap: 10px;
  flex: 1;
}

.function-options .q-btn {
  flex: 1;
}
</style>