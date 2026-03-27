import { createApp } from 'vue'
import App from './App.vue'

// --- 核心修复：引入 Element Plus 组件库与样式 ---
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

const app = createApp(App)

// --- 挂载插件 ---
app.use(ElementPlus)

app.mount('#app')