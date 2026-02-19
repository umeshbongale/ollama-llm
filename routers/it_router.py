from fastapi import APIRouter
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel
from it.it_service import generate_it_response

router = APIRouter()


class ITRequest(BaseModel):
    message: str


# ==============================
# IT UI
# ==============================

@router.get("/it", response_class=HTMLResponse)
def it_home():
    return """
<!DOCTYPE html>
<html>
<head>
<title>IT Support Assistant</title>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<meta name="viewport" content="width=device-width, initial-scale=1" />

<style>
body {
    margin:0;
    background:#343541;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    color:white;
    font-size:18px;
}

.chat-container {
    max-width:900px;
    margin:auto;
    height:100vh;
    display:flex;
    flex-direction:column;
}

.chat-header {
    padding:20px;
    background:#202123;
    font-size:22px;
    font-weight:600;
}

.chat-box {
    flex:1;
    overflow-y:auto;
    padding:30px;
    display:flex;
    flex-direction:column;
    gap:25px;
}

.message {
    max-width:75%;
    padding:18px 20px;
    border-radius:16px;
    line-height:1.6;
    font-size:18px;
}

.user {
    background:#10a37f;
    align-self:flex-end;
}

.bot {
    background:#444654;
    align-self:flex-start;
}

.input-area {
    display:flex;
    padding:20px;
    background:#202123;
    border-top:1px solid #3a3b47;
}

input {
    flex:1;
    padding:16px;
    border:none;
    border-radius:10px;
    background:#40414f;
    color:white;
    font-size:18px;
}

input:focus {
    outline:none;
}

button {
    margin-left:15px;
    padding:16px 20px;
    border:none;
    border-radius:10px;
    background:#10a37f;
    color:white;
    font-size:18px;
    cursor:pointer;
}

button:hover {
    background:#0d8c6c;
}
</style>
</head>

<body>

<div class="chat-container">

    <div class="chat-header">
        💻 IT Support Assistant
    </div>

    <div id="chatBox" class="chat-box"></div>

    <div class="input-area">
        <input type="text" id="messageInput"
        placeholder="Describe your IT issue..."
        onkeypress="if(event.key==='Enter') sendMessage()" />
        <button onclick="sendMessage()">Send</button>
    </div>

</div>

<script>

async function sendMessage(){

    const input = document.getElementById("messageInput");
    const message = input.value.trim();
    if(!message) return;

    const chatBox = document.getElementById("chatBox");

    const userDiv = document.createElement("div");
    userDiv.className="message user";
    userDiv.innerText=message;
    chatBox.appendChild(userDiv);

    input.value="";
    chatBox.scrollTop = chatBox.scrollHeight;

    const response = await fetch("/it/ask",{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({message:message})
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");

    const botDiv = document.createElement("div");
    botDiv.className="message bot";
    chatBox.appendChild(botDiv);

    let fullText="";

    while(true){
        const {done,value}=await reader.read();
        if(done) break;

        const chunk=decoder.decode(value);
        fullText+=chunk;
        botDiv.innerHTML = marked.parse(fullText);
        chatBox.scrollTop=chatBox.scrollHeight;
    }
}

</script>

</body>
</html>
"""


# ==============================
# IT ASK ENDPOINT
# ==============================

@router.post("/it/ask")
async def it_ask(req: ITRequest):

    return StreamingResponse(
        generate_it_response(req.message),
        media_type="text/plain"
    )
