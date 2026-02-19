from fastapi import APIRouter
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel
from finance.finance_service import generate_finance_response

router = APIRouter()


class FinanceRequest(BaseModel):
    message: str


@router.get("/finance", response_class=HTMLResponse)
def finance_home():
    return """
<!DOCTYPE html>
<html>
<head>
<title>Finance Support Assistant</title>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<meta name="viewport" content="width=device-width, initial-scale=1" />
<style>
body { margin:0; background:#343541; font-family:sans-serif; color:white; font-size:18px;}
.chat-container { max-width:900px; margin:auto; height:100vh; display:flex; flex-direction:column;}
.chat-header { padding:20px; background:#202123; font-size:22px; font-weight:600;}
.chat-box { flex:1; overflow-y:auto; padding:30px; display:flex; flex-direction:column; gap:25px;}
.message { max-width:75%; padding:18px; border-radius:16px; line-height:1.6;}
.user { background:#10a37f; align-self:flex-end;}
.bot { background:#444654; align-self:flex-start;}
.input-area { display:flex; padding:20px; background:#202123;}
input { flex:1; padding:16px; border:none; border-radius:10px; background:#40414f; color:white;}
button { margin-left:15px; padding:16px; border:none; border-radius:10px; background:#10a37f; color:white;}
</style>
</head>
<body>
<div class="chat-container">
<div class="chat-header">💰 Finance Support Assistant</div>
<div id="chatBox" class="chat-box"></div>
<div class="input-area">
<input type="text" id="messageInput" placeholder="Ask your finance question..."
onkeypress="if(event.key==='Enter') sendMessage()" />
<button onclick="sendMessage()">Send</button>
</div>
</div>
<script>
async function sendMessage(){
const input=document.getElementById("messageInput");
const message=input.value.trim();
if(!message) return;
const chatBox=document.getElementById("chatBox");
const userDiv=document.createElement("div");
userDiv.className="message user";
userDiv.innerText=message;
chatBox.appendChild(userDiv);
input.value="";
const response=await fetch("/finance/ask",{method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({message:message})});
const reader=response.body.getReader();
const decoder=new TextDecoder("utf-8");
const botDiv=document.createElement("div");
botDiv.className="message bot";
chatBox.appendChild(botDiv);
let fullText="";
while(true){
const {done,value}=await reader.read();
if(done) break;
fullText+=decoder.decode(value);
botDiv.innerHTML=marked.parse(fullText);
}
}
</script>
</body>
</html>
"""


@router.post("/finance/ask")
async def finance_ask(req: FinanceRequest):
    return StreamingResponse(
        generate_finance_response(req.message),
        media_type="text/plain"
    )
