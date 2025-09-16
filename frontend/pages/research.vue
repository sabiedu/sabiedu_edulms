<template>
  <div class="min-h-screen bg-gray-50">
    <header class="bg-white shadow">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center py-6">
          <div>
            <h1 class="text-3xl font-bold text-gray-900">Research Assistant</h1>
            <p class="mt-1 text-sm text-gray-500">AI-powered academic research and literature review</p>
          </div>
          <NuxtLink to="/dashboard" class="text-gray-500 hover:text-gray-700">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m0 7h18"></path>
            </svg>
          </NuxtLink>
        </div>
      </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Research Query -->
      <div class="bg-white shadow rounded-lg p-6 mb-8">
        <h2 class="text-lg font-medium text-gray-900 mb-4">Start Research</h2>
        
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Research Query</label>
            <textarea v-model="researchQuery" rows="3" 
                     class="w-full border border-gray-300 rounded-md px-3 py-2"
                     placeholder="Enter your research question or topic..."></textarea>
          </div>
          
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Research Type</label>
              <select v-model="researchType" class="w-full border border-gray-300 rounded-md px-3 py-2">
                <option value="academic_search">Academic Search</option>
                <option value="literature_review">Literature Review</option>
                <option value="citation_analysis">Citation Analysis</option>
                <option value="trend_analysis">Trend Analysis</option>
              </select>
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Depth</label>
              <select v-model="researchDepth" class="w-full border border-gray-300 rounded-md px-3 py-2">
                <option value="quick">Quick Overview</option>
                <option value="standard">Standard</option>
                <option value="comprehensive">Comprehensive</option>
              </select>
            </div>
          </div>
          
          <button @click="startResearch" :disabled="researching || !researchQuery.trim()"
                  class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50">
            {{ researching ? 'Researching...' : 'Start Research' }}
          </button>
        </div>
      </div>

      <!-- Research Results -->
      <div v-if="researchResults" class="bg-white shadow rounded-lg p-6 mb-8">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Research Results</h3>
        
        <div class="space-y-6">
          <!-- Summary -->
          <div v-if="researchResults.summary" class="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h4 class="font-medium text-blue-900 mb-2">Research Summary</h4>
            <p class="text-blue-800">{{ researchResults.summary }}</p>
          </div>
          
          <!-- Key Findings -->
          <div v-if="researchResults.key_findings" class="bg-green-50 border border-green-200 rounded-lg p-4">
            <h4 class="font-medium text-green-900 mb-2">Key Findings</h4>
            <ul class="list-disc list-inside text-green-800 space-y-1">
              <li v-for="finding in researchResults.key_findings" :key="finding">{{ finding }}</li>
            </ul>
          </div>
          
          <!-- Sources -->
          <div v-if="researchResults.sources" class="space-y-4">
            <h4 class="font-medium text-gray-900">Sources Found</h4>
            <div v-for="source in researchResults.sources" :key="source.id" 
                 class="border border-gray-200 rounded-lg p-4">
              <h5 class="font-medium text-gray-900">{{ source.title }}</h5>
              <p class="text-sm text-gray-600 mt-1">{{ source.authors?.join(', ') }}</p>
              <p class="text-sm text-gray-500 mt-1">{{ source.publication_date }}</p>
              <p class="text-gray-700 mt-2">{{ source.abstract }}</p>
              <div class="mt-3 flex items-center space-x-4">
                <span class="text-sm text-gray-500">Relevance: {{ source.relevance_score }}/10</span>
                <span class="text-sm text-gray-500">Citations: {{ source.citation_count }}</span>
              </div>
            </div>
          </div>
        </div>
        
        <div class="mt-6 flex justify-end space-x-3">
          <button @click="exportResults" class="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700">
            Export Results
          </button>
          <button @click="generateContent" class="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700">
            Generate Content
          </button>
        </div>
      </div>

      <!-- Research History -->
      <div class="bg-white shadow rounded-lg p-6">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Research History</h3>
        
        <div class="space-y-4">
          <div v-for="research in researchHistory" :key="research.id" 
               class="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
            <div>
              <h4 class="font-medium text-gray-900">{{ research.query }}</h4>
              <p class="text-sm text-gray-500">{{ research.type }} • {{ research.date }}</p>
            </div>
            <div class="text-right">
              <div class="text-sm text-gray-500">{{ research.sources_found }} sources</div>
              <button @click="loadResearch(research)" class="text-blue-600 hover:text-blue-800 text-sm">
                View Results
              </button>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  middleware: 'auth'
})

const config = useRuntimeConfig()
const apiBase = config.public.apiBase as string

// Research form
const researchQuery = ref('')
const researchType = ref('academic_search')
const researchDepth = ref('standard')
const researching = ref(false)

// Results
const researchResults = ref(null)

// History (mock data)
const researchHistory = ref([
  {
    id: 1,
    query: 'Machine Learning in Education',
    type: 'Literature Review',
    date: '2 days ago',
    sources_found: 15
  },
  {
    id: 2,
    query: 'AI Ethics in Learning Systems',
    type: 'Academic Search',
    date: '1 week ago',
    sources_found: 8
  }
])

const startResearch = async () => {
  researching.value = true
  
  try {
    const response = await fetch(`${apiBase}/agents/messages`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        channel: 'research',
        senderAgent: 'frontend',
        message: {
          query: researchQuery.value,
          research_type: researchType.value,
          depth: researchDepth.value
        }
      })
    })
    
    const data = await response.json()
    
    if (data.success) {
      researchResults.value = data.results
    } else {
      throw new Error(data.error || 'Research failed')
    }
  } catch (error) {
    console.error('Research failed:', error)
    alert('Research failed: ' + error.message)
  } finally {
    researching.value = false
  }
}

const exportResults = () => {
  if (!researchResults.value) return
  
  const dataStr = JSON.stringify(researchResults.value, null, 2)
  const dataBlob = new Blob([dataStr], { type: 'application/json' })
  const url = URL.createObjectURL(dataBlob)
  
  const link = document.createElement('a')
  link.href = url
  link.download = `research_results_${Date.now()}.json`
  link.click()
  
  URL.revokeObjectURL(url)
}

const generateContent = async () => {
  if (!researchResults.value) return
  
  // Navigate to content generation with research data
  await navigateTo({
    path: '/content-generation',
    query: { research: JSON.stringify(researchResults.value) }
  })
}

const loadResearch = (research: any) => {
  // Load previous research results
  researchQuery.value = research.query
  researchType.value = research.type.toLowerCase().replace(' ', '_')
}
</script>
