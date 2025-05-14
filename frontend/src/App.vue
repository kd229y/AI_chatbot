<template>
    <div id="container"> <!--d-flex flex-column align-items-center min-vh-100 bg-light p-4-->
        <!-- 標題 -->
        <h1 class="">RAG 聊天系統</h1> <!--text-primary mb-4-->

        <!-- 聊天框 -->
        <div id="chat-space">
            <!--w-100 max-w-3xl bg-white shadow rounded p-4 h-500 overflow-auto border border-secondary position-relative-->



            <!-- 右上角：清除聊天 -->
            <button id="clear-chat" @click="clearChat"> <!--position-absolute top-0 end-0 m-2 btn btn-danger btn-sm-->
                清除聊天
            </button>

            <!-- 聊天內容 -->
            <div v-for="message in messages" :key="message.id"
                :class="message.sender === 'User' ? 'user-message' : 'bot-message'">
                <!--p-3 my-2 rounded w-75 mx-auto-->
                <!--<strong class="text-dark">{{ message.sender }}:</strong>-->
                <p v-html="message.text"></p> <!-- 這裡用 v-html 來顯示解析後的 HTML -->
            </div>
        </div>

        <!-- 底部輸入框 -->
        <div id="user-input-area"> <!--w-100 max-w-3xl mt-4 d-flex gap-2-->
            <input v-model="userMessage" id="user-input-text" placeholder="請輸入你的消息..." @keyup.enter="sendMessage" />
            <button id="send-msg-btn" @click="sendMessage">
                <img src="send.jpg" width="100%" height="100%">
            </button>

            <!-- 上傳檔案 -->
            <input type="file" id="file-upload" @change="handleFileUpload" />
            <!--position-absolute top-0 start-0 m-2 btn btn-outline-secondary btn-sm-->
        </div>
    </div>
</template>

<script>
import axios from "axios";
import { marked } from "marked";

export default {
    data() {
        return {
            userMessage: "",
            messages: [],
        };
    },
    methods: {
        sendMessage() {
            if (this.userMessage.trim() === "") return;

            const userMsg = this.userMessage;
            this.messages.push({ id: Date.now(), sender: "User", text: userMsg });

            axios
                .post("http://localhost:5000/respond", { user_message: userMsg })
                .then((response) => {
                    const botMessage = response.data.bot_message;
                    const formattedMessage = marked(botMessage); // 解析 Markdown

                    this.messages.push({ id: Date.now(), sender: "Your waiter", text: formattedMessage });
                })
                .catch((error) => {
                    console.error("Error sending message:", error);
                });

            this.userMessage = "";
        },

        handleFileUpload(event) {
            const formData = new FormData();
            formData.append("file", event.target.files[0]);

            axios
                .post("http://localhost:5000/upload", formData)
                .then((response) => {
                    alert(response.data);
                })
                .catch((error) => {
                    console.error("Error uploading file:", error);
                });
        },

        clearChat() {
            this.messages = [];
        },
    },
};
</script>

<style scoped>
@import url('https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css');

#container {
    display: flex;
    flex-direction: column;
    align-items: center;
    min-height: 100vh;
    background-color: white;
    width: 100%;
}

#chat-space {
    width: 100%;
    background-color: white;
    height: 750px;
    overflow: auto;
    border: none;
    position: relative;
}

#clear-chat {
    position: absolute;
    width: 50px;
    height: 50px;
}

.user-message {
    position: relative;
    background-color: #bbb;
    color: black;
    padding: 20px;
    border: none;
    border-radius: 30px;
    margin-left: auto;
    text-align: center;
    max-width: 300px;
}

.bot-message {
    background: none;
    color: black;
    padding: 20px;
    border: none;
    margin-right: auto;
    text-align: center;
    max-width: 300px;
}

#user-input-area {
    width: 80%;
    border-radius: 30px;
}

#user-input-text {
    width: calc(100% - 20px);
    border-radius: 20px;
}

#send-msg-btn {
    width: 20px;
    height: 20px;
}

#file-upload {
    position: absolute;
    width: 50px;
    height: 50px;
}

.h-500 {
    height: 500px;
}
</style>