<template>
  <div class="navigation-box">
    <div class="top-row">
      <q-icon name="liquor" size="32px" color="github-zero"/>
      <span class="title">cocktail-compiler</span>
      <q-btn color="github-seven" text-color="github-zero" dense icon="close"></q-btn>
    </div>
    <div class="page-options">
      <q-btn color="github-seven" text-color="github-zero" label="Bartender Functionality" class="full-width"></q-btn>
      <q-btn color="github-seven" text-color="github-zero" label="Ingredient List" class="full-width"></q-btn>
      <q-btn color="github-seven" text-color="github-zero" label="Discover Cocktails" class="full-width"></q-btn>
      <q-btn color="github-seven" text-color="github-zero" label="Troubleshooting" class="full-width"></q-btn>
    </div>
  </div>
</template>

<script></script>

<style scoped>
.navigation-box {
  width: 100%;
  box-sizing: border-box;
  outline: 2px solid #f0f6fc;
  padding: 20px;
  background-color: #30363d;
}

.top-row {
  display: flex;
  align-items: center;
}

.title {
  padding-left: 5px;
  color: #f0f6fc;
  font-size: 24px;
  font-weight: bold;
  flex: 1;
}

.page-options {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 10px;
}
</style>
