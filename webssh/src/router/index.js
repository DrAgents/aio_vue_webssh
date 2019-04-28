import Vue from "vue";
import Router from "vue-router";
import WebSSH from "@/components/WebSSH";
import Hello from "@/components/Hello";

Vue.use(Router);

export default new Router({
  routes: [
    {
      path: "/",
      name: "WebSSH",
      component: WebSSH
    },
    {
      path: "/hello",
      name: "Hello",
      component: Hello
    }
  ]
});
