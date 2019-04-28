<template>
  <div>
    <input v-model="host" placeholder="host">
    <input v-model="port" placeholder="port">
    <input v-model="username" placeholder="username">
    <input v-model="password" placeholder="password">
    <button @click="connect()">连接</button>
    <div class="console" id="terminal"></div>
  </div>
</template>
<script>
import Terminal from "./Xterm";
export default {
  name: "Console",
  props: {
    terminal: {
      type: Object,
      default: {}
    }
  },
  data() {
    return {
      term: null,
      terminalSocket: null,
      host: null,
      port: null,
      username: null,
      password: null,
    };
  },
  methods: {
    runRealTerminal() {
      console.log("webSocket is finished");
    },
    errorRealTerminal() {
      console.log("error");
    },
    closeRealTerminal() {
      console.log("close");
    },
    connect() {
      console.log("pid : " + this.terminal.pid + " is on ready");
      let terminalContainer = document.getElementById("terminal");
      this.term = new Terminal();
      this.term.open(terminalContainer);
      // open websocket
      let url = `ws://localhost:3000/terminals/?host=${this.host}&port=${this.port}&username=${this.username}&password=${this.password}`;

      this.terminalSocket = new WebSocket(url);
      this.terminalSocket.onopen = this.runRealTerminal;
      this.terminalSocket.onclose = this.closeRealTerminal;
      this.terminalSocket.onerror = this.errorRealTerminal;
      this.term.attach(this.terminalSocket);
      this.term._initialized = true;
      console.log("mounted is going on");
    }
  },
  mounted() {
  },
  beforeDestroy() {
    if (this.terminalSocket) {
      this.terminalSocket.close();
      this.term.destroy();
    }
  }
};
</script>