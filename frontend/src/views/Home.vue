<template>
  <div>
    <h1>Welcome</h1>
    <p>Hi, {{ username }}</p>
    <input type="button" value="Logout" @click="logout" />
    <br />
    <input type="button" value="Notify me!" @click="notify" />
  </div>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import * as auth from "@/lib/auth";

@Component
export default class Hello extends Vue {
  username: string = "";

  mounted() {
    this.$http.get("auth/me").then(response => {
      this.username = response.text();
    });
  }

  logout() {
    auth.logout();
    this.$router.push({ name: "auth" });
  }

  notify() {
      this.$http.get("auth/notify").then(x => {console.log(x);});
  }
}
</script>
