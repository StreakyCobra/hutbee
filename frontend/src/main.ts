import Vue from "vue";
import App from "./App.vue";
import "./registerServiceWorker";
import router from "./router";
import VueResource from "vue-resource";

Vue.config.productionTip = false;

Vue.use(VueResource);
(Vue as any).http.options.root = process.env.VUE_APP_API_ROOT;

new Vue({
  router,
  render: h => h(App)
}).$mount("#app");
