<template>
  <div>
    <h1>Welcome</h1>
    <p>What is your name?</p>
    <input v-model="name" type="text" />
    <div>Answer from the API: {{answer}}</div>
  </div>
</template>


<script lang="ts">
import { Component, Watch, Vue } from "vue-property-decorator";

@Component
export default class Hello extends Vue {
  name: string = ""
  answer: string = ""

  mounted() {
    this.call_api(this.name);
  }

  @Watch("name")
  onPropertyChanged(value: string, oldValue:string) {
    this.call_api(value);
  }

  call_api(value: string) {
    var url = ""
    if (value) {
      url += '?name=' + this.name
    }
    this.$http.get(url).then(response => {
        return response.text();
      }, response => {
        this.answer = "error";
      }).then(response => {
        this.answer = response || "API call failed"
      });
      }
}
</script>