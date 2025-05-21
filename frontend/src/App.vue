<template>
  <div class="container-fluid vh-100 p-3 d-flex">
    <!-- 左側：Session 列表 -->
    <aside class="col-3 bg-light border-end p-3 d-flex flex-column">
      <h5 class="mb-3">聊天會話</h5>
      <ul class="list-group mb-3 flex-grow-1 overflow-auto">
        <li
          v-for="sess in sessions"
          :key="sess.id"
          :class="['list-group-item', currentSessionId === sess.id ? 'active' : '']"
          class="d-flex justify-content-between align-items-center"
          @click="selectSession(sess.id)"
        >
          {{ sess.title }}
          <button class="btn btn-sm btn-outline-danger" @click.stop="deleteSession(sess.id)">×</button>
        </li>
      </ul>
      <div class="input-group">
        <input v-model="newTitle" class="form-control" placeholder="新會話標題" @keyup.enter="createSession" />
        <button class="btn btn-primary" @click="createSession">新增</button>
      </div>
    </aside>

    <!-- 右側：Chat 視窗 -->
    <section class="col-9 d-flex flex-column">
      <h3 class="text-primary mb-3">AI Chatbot</h3>

      <!-- 聊天內容 -->
      <div class="flex-grow-1 bg-white border rounded p-3 overflow-auto position-relative">
        <!-- 右上：清除對話框 -->
        <button
          class="position-absolute top-0 end-0 m-2 btn btn-danger btn-sm"
          @click="clearMessages"
        >清除對話</button>

        <div v-for="msg in messages" :key="msg.id" class="mb-2 w-75 mx-auto"
          :class="msg.role === 'user' ? 'text-end bg-light rounded p-2' : 'text-start bg-white rounded p-2 border'">
          <strong>{{ msg.role === 'user' ? 'User' : 'Assistant' }}：</strong>
          <div v-html="msg.html"></div>
        </div>
      </div>

      <!-- 輸入區 -->
      <div class="input-group mt-3">
        <input
          v-model="userInput"
          @keyup.enter="sendMessage"
          class="form-control"
          placeholder="輸入訊息並按 Enter"
        />
        <button class="btn btn-primary" @click="sendMessage">發送</button>
      </div>
    </section>
  </div>

</template>



<script setup>
import { ref, onMounted, watch } from 'vue'
import axios from 'axios'
import { marked } from 'marked'

const sessions = ref([])
const currentSessionId = ref(null)
const messages = ref([])
const newTitle = ref('')
const userInput = ref('')

// 從後端讀取所有 Session
async function loadSessions() {
  const res = await axios.get('http://127.0.0.1:8000/sessions')
  sessions.value = res.data
  if (!currentSessionId.value && sessions.value.length) {
    currentSessionId.value = sessions.value[0].id
  }
}

// 切換 Session 時讀取訊息
async function loadMessages(sessionId) {
  if (!sessionId) return
  const res = await axios.get('http://127.0.0.1:8000/messages', {
    params: { session_id: sessionId }
  })
  messages.value = res.data.map(m => ({
    id: m.id,
    role: m.role,
    html: marked(m.content)
  }))
}

// 選擇 Session
function selectSession(id) {
  currentSessionId.value = id
}

// 新增 Session
async function createSession() {
  if (!newTitle.value.trim()) return
  const res = await axios.post('http://127.0.0.1:8000/sessions', { title: newTitle.value })
  sessions.value.push(res.data)
  newTitle.value = ''
}

// 刪除 Session
async function deleteSession(id) {
  await axios.delete(`http://127.0.0.1:8000/sessions/${id}`)
  sessions.value = sessions.value.filter(s => s.id !== id)
  if (currentSessionId.value === id) {
    currentSessionId.value = sessions.value.length ? sessions.value[0].id : null
  }
}

// 傳送訊息到 /chat
async function sendMessage() {
  if (!userInput.value.trim() || !currentSessionId.value) return
  if (!currentSessionId.value) {
  alert('請先選擇一個對話 session')
  return
}
  // 顯示 user
  messages.value.push({
    id: Date.now(),
    role: 'user',
    html: marked(userInput.value)
  })

  // 呼叫後端
  const res = await axios.post(`http://127.0.0.1:8000/chat?session_id=${currentSessionId.value}`, {
    model: 'llama3.2',
    messages: [{ role: 'user', content: userInput.value }]
  })
  const reply = res.data.message

  messages.value.push({
    id: Date.now() + 1,
    role: reply.role,
    html: marked(reply.content)
  })

  userInput.value = ''
}

// 清除聊天視窗但不影響後端資料
function clearMessages() {
  messages.value = []
}

// 初始化
onMounted(async () => {
  await loadSessions()
})

// 當切換 session 時，自動讀取訊息
watch(currentSessionId, async (newId) => {
  await loadMessages(newId)
})
</script>

<style>
@import url('https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css');
</style>
