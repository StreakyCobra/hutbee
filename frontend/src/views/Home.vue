<template>
    <div>
        <h1>Welcome</h1>
        <p>Hi, {{ username }}</p>
        <input type="button" value="Logout" @click="logout"/>
    </div>
</template>


<script lang="ts">
    import {Component, Vue} from "vue-property-decorator";
    import * as auth from "@/lib/auth"

    @Component
    export default class Hello extends Vue {
        username: string = "";

        mounted() {
            this.$http.get('me').then(response => {
                response.text().then(data => {
                    this.username = data;
                });
            })
        }

        logout() {
            auth.logout();
            this.$router.push({"name": "auth"});
        }
    }
</script>