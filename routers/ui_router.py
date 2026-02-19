from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
def home():
    return """
<!DOCTYPE html>
<html>
<head>
<title>AI Sales Agent</title>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<style>
body { margin:0; background:#343541; font-family:Arial; color:white; }
.chat-container { max-width:900px; margin:auto; height:100vh; display:flex; flex-direction:column; }
.chat-header { padding:20px; background:#202123; font-size:20px; }
.chat-box { flex:1; overflow-y:auto; padding:20px; display:flex; flex-direction:column; gap:20px; }
.message { max-width:80%; padding:15px; border-radius:10px; }
.user { background:#444654; align-self:flex-end; }
.bot { background:#3e3f4b; align-self:flex-start; }
.product-card { background:#2a2b32; padding:15px; border-radius:8px; margin-top:10px; }
button { margin-top:10px; padding:8px 14px; border:none; border-radius:5px; background:#10a37f; color:white; cursor:pointer; }
button:hover { background:#0d8c6c; }
.input-area { display:flex; padding:15px; background:#202123; }
input { flex:1; padding:12px; border:none; border-radius:5px; background:#40414f; color:white; }
</style>
</head>
<body>

<div class="chat-container">
<div class="chat-header">🤖 AI Sales Agent</div>
<div id="chatBox" class="chat-box"></div>

<div class="input-area">
<input type="text" id="messageInput"
placeholder="Ask for a product..."
onkeypress="if(event.key==='Enter') sendMessage()" />
<button onclick="sendMessage()">Send</button>
</div>
</div>

<script>

let sessionId = crypto.randomUUID();

async function sendMessage(customMessage=null){

    const input = document.getElementById("messageInput");
    const message = customMessage ? customMessage : input.value.trim();
    if(!message) return;

    const chatBox = document.getElementById("chatBox");

    const userDiv = document.createElement("div");
    userDiv.className="message user";
    userDiv.innerText=message;
    chatBox.appendChild(userDiv);

    input.value="";

    const response = await fetch("/ask",{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({message:message, session_id:sessionId})
    });

    const contentType = response.headers.get("content-type");

    const botDiv = document.createElement("div");
    botDiv.className="message bot";
    chatBox.appendChild(botDiv);

    if(contentType.includes("application/json")){
        const data = await response.json();

        if(data.type === "product_list"){
            botDiv.innerHTML = `<b>${data.category} Products:</b>`;
            data.products.forEach(p=>{
                botDiv.innerHTML += `
                <div class="product-card">
                    <b>${p.name}</b><br>
                    Price: ₹${p.price}<br>
                    <button onclick="sendMessage('order_${p.index}')">
                        Place Order
                    </button>
                </div>`;
            });
        }
        else if(data.type === "order_confirmed"){
            botDiv.innerHTML = `
            <b>✅ Order Confirmed</b><br>
            Product: ${data.product}<br>
            Price: ₹${data.price}<br>
            Quantity: ${data.quantity}<br>
            Total: ₹${data.total}<br>
            Address: ${data.address}`;
        }
        else{
            botDiv.innerHTML = marked.parse(data.response);
        }

        chatBox.scrollTop=chatBox.scrollHeight;
        return;
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");

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
