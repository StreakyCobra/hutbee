<template>
  <div>
    <h1>Login</h1>
    <p>What is your name?</p>
    <input v-model="username" type="text" />
    <input v-model="password" type="password" />
    <input type="button" value="Login" @click="login" />
  </div>
</template>

<script lang="ts">
import { Component, Watch, Vue } from "vue-property-decorator";
import * as auth from "@/lib/auth";

@Component
export default class Auth extends Vue {
  username: string = "";
  password: string = "";

  login() {
    this.$http
      .post("auth/login", {
        username: this.username,
        password: this.password
      })
      .then(
        response => {
          response.json().then((data: { [x: string]: string }) => {
            console.log("Authentication successful");
            auth.login(data);
            this.$router.push({ name: "home" });
          });
        },
        response => {
          this.username = "";
          this.password = "";
          console.log("Authentication error");
        }
      );
  }

  logout() {
    auth.logout();
  }
}
</script>
