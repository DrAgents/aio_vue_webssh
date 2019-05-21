<template>
  <div>
    <div>
      <input v-model="host" placeholder="host">
      <input v-model="port" placeholder="port">
      <input v-model="username" placeholder="username">
      <input v-model="password" placeholder="password">
      <button @click="connect()">连接</button>
    </div>
    <div>
      <input v-model="token" placeholder="输入 token, 即 openid">
      <button @click="connect_token()">连接</button>
    </div>
    <div>
      <input v-model="console.width" placeholder="width">
      <input v-model="console.height" placeholder="height">
      <button @click="resizeTerminal()">更改终端大小</button>
    </div>
    <div class="console" id="terminal"></div>
  </div>
</template>

<script>
import Terminal from "./Xterm";
import * as fit from "xterm/lib/addons/fit/fit";
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
      token: null,
      console: {
        width: "600px",
        height: "400px"
      }
    };
  },
  methods: {
    resizeTerminal() {
      // 调整 pty 的大小, 以便适应 div 的大小
      let terminalContainer = document.getElementById("terminal");
      terminalContainer.style.width = this.console.width;
      terminalContainer.style.height = this.console.height;
      this.term.fit();  // 自动调整前端界面的终端大小

      let result = fit.proposeGeometry(this.term);
      console.log(result);
      let command_data = {
        command: "resize",
        kwargs: result
      };
      this.terminalSocket.send("JSON:" + JSON.stringify(command_data)); // 发送特殊命令, 调整后台终端大小
    },
    runRealTerminal(event) {
      // 启动的时候, 清空输出, 并调整大小
      this.terminalSocket.send("clear\n");
      this.resizeTerminal();
      console.log("webSocket is started");
    },
    errorRealTerminal() {
      console.log("error");
    },
    closeRealTerminal() {
      console.log("close");
    },
    connect() {
      this.destroy_term();
      console.log("pid : " + this.terminal.pid + " is on ready");
      let terminalContainer = document.getElementById("terminal");

      this.term = new Terminal({
        rows: 24, // 行数
        cols: 80, // 列数, 以字符计算
        lineHeight: 1, // 行高
        fontSize: 20, // 字体大小
        fontFamily: "Consolas, courier-new, courier, monospace", // 字体
        // rendererType: 'dom',  // 渲染格式, dom 或 canvas
        theme: {
          // 主题选项
          background: "#002832", // 背景色
          foreground: "#4F747D", // 前景色
          selection: "#77999999", // 选中后的颜色
          cursor: "#aaa" // 光标颜色
        }
      });

      this.term.open(terminalContainer);

      // open websocket
      let url = `ws://localhost:3000/terminals/?host=${this.host}&port=${
        this.port
      }&username=${this.username}&password=${this.password}`;

      this.terminalSocket = new WebSocket(url);
      this.terminalSocket.onopen = this.runRealTerminal;
      this.terminalSocket.onclose = this.closeRealTerminal;
      this.terminalSocket.onerror = this.errorRealTerminal;

      this.term.attach(this.terminalSocket);
      console.log("mounted is going on");
    },
    connect_token() {
      this.destroy_term();
      let terminalContainer = document.getElementById("terminal");
      this.term = new Terminal();
      this.term.open(terminalContainer);
      let url = `wss://wx.piaoshiyun.com/ws/shell/token?openid=${this.token}`;

      this.terminalSocket = new WebSocket(url);
      this.terminalSocket.onopen = this.runRealTerminal;
      this.terminalSocket.onclose = this.closeRealTerminal;
      this.terminalSocket.onerror = this.errorRealTerminal;

      this.term.attach(this.terminalSocket);
      console.log("mounted is going on");
    },
    destroy_term() {
      if (this.terminalSocket) {
        this.terminalSocket.close();
        this.term.destroy();
      }
    }
  },
  mounted() {},
  beforeDestroy() {
    this.destroy_term();
  }
};
</script>

<style>
</style>

