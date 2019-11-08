<template>
  <div id="app">
    <router-view v-if="authenticated || isAuth()" />
  </div>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import * as auth from "@/lib/auth";

@Component
export default class App extends Vue {
  authenticated: boolean = false;

  mounted() {
    this.checkAuth();
    this.$router.afterEach(() => {
      this.checkAuth();
    });
  }

  isAuth() {
    return this.$route.name == "auth";
  }

  checkAuth() {
    auth.isConnected(
      this.$http,
      () => {
        this.authenticated = true;
      },
      () => {
        this.authenticated = false;
        this.$router.push({ name: "auth" });
      }
    );
  }
}
</script>
