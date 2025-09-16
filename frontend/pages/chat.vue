<template>
  <div class="min-h-screen flex flex-col bg-gray-50">
    <header class="border-b bg-white">
      <div class="max-w-4xl mx-auto px-4 py-3 flex items-center justify-between">
        <h1 class="text-xl font-semibold">EduLMS Tutor Chat</h1>
        <div class="flex items-center gap-2 text-sm">
          <span :class="[
              'inline-block h-2.5 w-2.5 rounded-full',
              health === 'healthy' ? 'bg-green-500' : health === 'unhealthy' ? 'bg-red-500' : 'bg-gray-300'
            ]" />
          <span class="text-gray-600">DB Health: {{ health }}</span>
        </div>
      </div>
    </header>

    <main class="flex-1">
      <div class="max-w-4xl mx-auto px-4 py-6">
        <div class="bg-white shadow rounded-lg p-4 h-[65vh] overflow-y-auto space-y-3">
          <div v-if="messages.length === 0" class="text-gray-500 text-sm">
            Start the conversation by sending a message. The Tutor Agent will reply here.
          </div>

          <div v-for="(m, idx) in messages" :key="idx" class="flex" :class="m.role === 'user' ? 'justify-end' : 'justify-start'">
            <div class="max-w-[80%] rounded-lg px-3 py-2 text-sm"
                 :class="m.role === 'user' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-800'">
              <div class="whitespace-pre-wrap">{{ m.text }}</div>
              <div class="text-[11px] mt-1 opacity-70">
                {{ new Date(m.ts).toLocaleTimeString() }}
              </div>
            </div>
          </div>
        </div>

        <form class="mt-4 flex gap-2" @submit.prevent="send">
          <input v-model="input" type="text" placeholder="Ask a question..."
                 class="flex-1 border rounded-lg px-3 py-2 focus:outline-none focus:ring focus:border-blue-300" />
          <button type="submit" :disabled="sending || input.trim().length === 0"
                  class="px-4 py-2 rounded-lg bg-blue-600 text-white disabled:opacity-50">
            {{ sending ? 'Sending...' : 'Send' }}
          </button>
        </form>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import { useRuntimeConfig } from 'nuxt/app'

const config = useRuntimeConfig()
const apiBase = config.public.apiBase as string

const input = ref('')
const messages = ref<Array<{ role: 'user' | 'agent', text: string, ts: string, id?: number }>>([])
const sending = ref(false)
const health = ref<'unknown' | 'healthy' | 'unhealthy'>('unknown')

let pollTimer: any = null
let healthTimer: any = null
const seenIds = new Set<number>()

async function send() {
  const text = input.value.trim()
  if (!text) return

  // Render immediately
  messages.value.push({ role: 'user', text, ts: new Date().toISOString() })
  input.value = ''
  sending.value = true

  try {
    await fetch(`${apiBase}/agents/messages`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        channel: 'demo',
        senderAgent: 'frontend',
        message: { text },
        recipientAgent: 'tutor-agent',
        priority: 5,
      }),
    })
  } catch (e) {
    console.error('Send failed', e)
  } finally {
    sending.value = false
  }
}

async function pollReplies() {
  try {
    const res = await fetch(`${apiBase}/agents/messages/demo/frontend?limit=10`)
    const json: any = await res.json()
    if (json && json.success && Array.isArray(json.data)) {
      for (const row of json.data) {
        const id = typeof row.id === 'number' ? row.id : Number(row.id)
        if (!Number.isNaN(id) && seenIds.has(id)) continue

        // message may be object or json string
        let text = ''
        try {
          const msg = typeof row.message === 'string' ? JSON.parse(row.message) : row.message
          if (msg && typeof msg.text === 'string') text = msg.text
        } catch (err) {
          console.warn('Failed parsing message JSON', err)
        }
        if (!text) continue

        messages.value.push({ role: 'agent', text, ts: row.created_at || new Date().toISOString(), id })
        if (!Number.isNaN(id)) seenIds.add(id)

        // Mark processed to avoid re-poll duplicates
        if (!Number.isNaN(id)) {
          try {
            await fetch(`${apiBase}/agents/messages/${id}/processed`, {
              method: 'PUT',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ processingAgent: 'frontend' })
            })
          } catch (err) {
            console.warn('Failed to mark processed', err)
          }
        }
      }
    }
  } catch (e) {
    console.error('Poll failed', e)
  }
}

async function checkHealth() {
  try {
    const res = await fetch(`${apiBase}/database/health`)
    const json: any = await res.json()
    health.value = json?.success ? 'healthy' : 'unhealthy'
  } catch {
    health.value = 'unhealthy'
  }
}

onMounted(() => {
  pollTimer = setInterval(pollReplies, 1500)
  healthTimer = setInterval(checkHealth, 5000)
  // initial fetch
  checkHealth()
  pollReplies()
})

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
  if (healthTimer) clearInterval(healthTimer)
})
</script>
