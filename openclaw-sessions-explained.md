# How Sessions Work in OpenClaw

This document explains OpenClaw's session and context management, based on our conversation about routing, memory, and multi-agent setups.

## 1. The Core Metaphor: Notebooks and Pages
To understand how OpenClaw remembers things, think of a physical notebook:
* **The Session Key (The Notebook):** This is the durable storage (a SQLite database file on the hard drive). It never changes for a specific room or DM. (e.g., `agent:main:discord:channel:1546538532...`)
* **The Session ID (The Page):** This is the specific "page" we are currently writing on. It represents the **Context** (the text actively sent to the AI model). (e.g., `d6b3cd81-812a...`)
* **The Message:** The actual text sent by a human or bot. Every message gets stamped with the current Session ID before being saved in the notebook. 

*Note: Real human users do not have Session IDs. The Session ID is purely an internal OpenClaw concept to manage the AI's memory.*

## 2. Gateway vs. Agent
It is crucial to understand that the "Agent" and the "Gateway" are two different layers:
* **The Gateway (The Mailroom):** Holds the API tokens, connects to Discord/Telegram, and catches incoming messages. It looks at its routing rules (`bindings`) to figure out who needs to see the message.
* **The Agent (The Worker):** Sits in a closed office with no internet connection to Discord. It only knows what is placed into its SQLite database by the Gateway.

## 3. How DMs vs. Group Channels Work
* **Direct Messages (DMs):** By default, OpenClaw collapses DMs from all platforms into **one single rolling session** (the "Main Session", key: `agent:main:main`). If you DM the agent on Discord, and then follow up in a Telegram DM, the agent has the exact same context.
* **Group Channels:** Rooms like Discord channels get their own isolated context (e.g., `agent:main:discord:channel:<id>`). The Main Session doesn't share a brain with this channel; it only gets compact "activity notices" about what happens here.

## 4. Multiple Agents in One Room
If you put multiple agents (e.g., `main`, `qa-engineer`, `developer`) in the same Discord channel, **they do not share a session.**
1. You send one message in Discord.
2. The Gateway receives it and sees three agents are assigned to the room.
3. The Gateway stamps the message with `main`'s Session ID and puts it in `main`'s SQLite database.
4. It does the same for `qa-engineer` and `developer`.

**Result:** One Discord message becomes three separate records. The agents' brains are 100% walled off from each other. They share a room, but they do not share a notebook.

## 5. What Happens When You Run `/new`?
When you type `/new` (or `/reset`):
* OpenClaw wipes the active **Context** (the pages we are currently looking at).
* It generates a new **Session ID**. 
* **The Session Key stays the same.**

This means the old chat history is *not* deleted. It is safely filed away in the SQLite database under the old Session ID. The AI starts with a clean slate to save tokens, but it can still use its memory search tools (`sessions_history`) to recall old conversations if asked. Furthermore, because it has a new Session ID, the Gateway will intentionally hide Discord's "recent message history" bundle from before the reset, ensuring the new session stays truly clean.

## 6. Bringing a New Agent Up to Speed
If you invite a brand new agent (Agent X) to an ongoing channel, it wakes up completely blank. The Gateway never stamped past messages into Agent X's database because Agent X wasn't in the room yet.

To catch them up, you can:
1. **Summarize it manually:** "Hey Agent X, we were just talking about..."
2. **Ask an existing agent to send context:** "Hey VanOpenClaw, bring Agent X up to speed." The existing agent can use its `sessions_send` tool to shoot a summary directly into Agent X's notebook behind the scenes.
3. **Agent X searches for it:** Agent X can use `sessions_history` to peek at another agent's notebook.

### The `tools.agentToAgent` Config
By default, cross-agent communication is turned **ON**. You do not need to add `tools.agentToAgent` to your config file to allow `sessions_send` to work. You only need to add it to your config if you want to *restrict* access (e.g., `enabled: false` or setting a specific `allow` list). If left unconfigured, every agent on the Gateway can talk to every other agent.