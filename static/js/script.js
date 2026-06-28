const sendButton = document.getElementById("send-btn");
const userInput = document.getElementById("user-input");
const chatBox = document.getElementById("chat-box");

// ---------- Add Message ----------
function addMessage(message, sender) {

    const messageDiv = document.createElement("div");
    messageDiv.classList.add("message", sender);

    if(sender === "user"){

        messageDiv.innerHTML = `
            <div class="bubble">
                <p>${message.replace(/\n/g,"<br>")}</p>
            </div>

            <div class="avatar user-avatar">
                A
            </div>
        `;

    }

    else{

        messageDiv.innerHTML = `
            <div class="avatar bot-avatar">
                AI
            </div>

            <div class="bubble">
               <p>${message.replace(/\n/g,"<br>")}</p>
            </div>
        `;

    }

    chatBox.appendChild(messageDiv);

    chatBox.scrollTop = chatBox.scrollHeight;
}

// ---------- Typing Animation ----------
function showTyping(){

    const typing = document.createElement("div");

    typing.classList.add("message","bot");

    typing.id = "typing";

    typing.innerHTML = `

        <div class="avatar bot-avatar">
            AI
        </div>

        <div class="bubble">

            <span class="dot"></span>
            <span class="dot"></span>
            <span class="dot"></span>

        </div>

    `;

    chatBox.appendChild(typing);

    chatBox.scrollTop = chatBox.scrollHeight;

}

function removeTyping(){

    const typing=document.getElementById("typing");

    if(typing){

        typing.remove();

    }

}

// ---------- Send Message ----------
async function sendMessage(){

    const message=userInput.value.trim();

    if(message==="") return;

    addMessage(message,"user");

    userInput.value="";

    showTyping();

    try{

        const response=await fetch("/chat",{

            method:"POST",

            headers:{
                "Content-Type":"application/json"
            },

            body:JSON.stringify({
                message:message
            })

        });

        const data=await response.json();

        removeTyping();

        const formatted = data.response.replace(/\n/g, "<br>");

        addMessage(formatted, "bot");

    }

    catch(error){

        removeTyping();

        addMessage("Something went wrong.","bot");

        console.log(error);

    }

}

// ---------- Button ----------
sendButton.addEventListener("click",sendMessage);

// ---------- Enter ----------
userInput.addEventListener("keydown",function(e){

    if(e.key==="Enter" && !e.shiftKey){

        e.preventDefault();

        sendMessage();

    }

});