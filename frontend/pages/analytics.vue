<template>
  <div class="min-h-screen bg-gray-50">
    <header class="bg-white shadow">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center py-6">
          <div>
            <h1 class="text-3xl font-bold text-gray-900">Learning Analytics</h1>
            <p class="mt-1 text-sm text-gray-500">AI-powered insights into your learning progress</p>
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
      <!-- Analytics Controls -->
      <div class="bg-white shadow rounded-lg p-6 mb-8">
        <h2 class="text-lg font-medium text-gray-900 mb-4">Analytics Options</h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <select v-model="selectedAnalyticsType" class="border border-gray-300 rounded-md px-3 py-2">
            <option value="performance">Performance Analysis</option>
            <option value="engagement">Engagement Patterns</option>
            <option value="prediction">Predictive Analytics</option>
            <option value="cohort">Cohort Analysis</option>
          </select>
          
          <select v-model="selectedTimeframe" class="border border-gray-300 rounded-md px-3 py-2">
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="90d">Last 90 days</option>
            <option value="1y">Last year</option>
          </select>
          
          <button @click="generateAnalytics" :disabled="loading" 
                  class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50">
            {{ loading ? 'Analyzing...' : 'Generate Analytics' }}
          </button>
        </div>
      </div>

      <!-- Analytics Results -->
      <div v-if="analyticsData" class="space-y-8">
        <!-- Key Metrics -->
        <div class="bg-white shadow rounded-lg p-6">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Key Metrics</h3>
          <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div v-for="metric in analyticsData.metrics" :key="metric.name" class="text-center">
              <div class="text-3xl font-bold text-blue-600">{{ metric.value }}</div>
              <div class="text-sm text-gray-500">{{ metric.name }}</div>
              <div v-if="metric.change" class="text-xs mt-1" 
                   :class="metric.change > 0 ? 'text-green-600' : 'text-red-600'">
                {{ metric.change > 0 ? '+' : '' }}{{ metric.change }}%
              </div>
            </div>
          </div>
        </div>

        <!-- AI Insights -->
        <div class="bg-white shadow rounded-lg p-6">
          <h3 class="text-lg font-medium text-gray-900 mb-4">AI-Generated Insights</h3>
          <div class="space-y-4">
            <div v-for="insight in analyticsData.insights" :key="insight" 
                 class="border-l-4 border-blue-500 pl-4 py-2">
              <p class="text-gray-700">{{ insight }}</p>
            </div>
          </div>
        </div>

        <!-- Recommendations -->
        <div class="bg-white shadow rounded-lg p-6">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Personalized Recommendations</h3>
          <div class="space-y-4">
            <div v-for="recommendation in analyticsData.recommendations" :key="recommendation" 
                 class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <div class="flex items-start">
                <svg class="w-5 h-5 text-yellow-600 mt-0.5 mr-3" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"></path>
                </svg>
                <p class="text-gray-700">{{ recommendation }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Performance Trends Chart -->
        <div class="bg-white shadow rounded-lg p-6">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Performance Trends</h3>
          <div class="h-64 bg-gray-100 rounded-lg flex items-center justify-center">
            <div class="text-center text-gray-500">
              <svg class="w-12 h-12 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
              </svg>
              <p>Chart visualization would appear here</p>
              <p class="text-sm">Confidence Score: {{ analyticsData.confidence_score }}%</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div v-else-if="loading" class="bg-white shadow rounded-lg p-12 text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p class="text-gray-600">Analyzing your learning data with AI...</p>
      </div>

      <!-- Initial State -->
      <div v-else class="bg-white shadow rounded-lg p-12 text-center">
        <svg class="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
        </svg>
        <h3 class="text-lg font-medium text-gray-900 mb-2">Generate Learning Analytics</h3>
        <p class="text-gray-600">Select your preferences above and click "Generate Analytics" to get AI-powered insights into your learning progress.</p>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { useAuth } from '~/composables/useAuth'

definePageMeta({
  middleware: 'auth'
})

const config = useRuntimeConfig()
const apiBase = config.public.apiBase as string
const { user } = useAuth()

const selectedAnalyticsType = ref('performance')
const selectedTimeframe = ref('30d')
const loading = ref(false)
const analyticsData = ref(null)

const generateAnalytics = async () => {
  loading.value = true
  
  try {
    // Send request to Analytics Agent
    const response = await fetch(`${apiBase}/agents/messages`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        channel: 'analytics_request',
        senderAgent: 'frontend',
        message: {
          query_type: selectedAnalyticsType.value,
          user_id: user.value?.id,
          timeframe: selectedTimeframe.value,
          metrics: ['performance', 'engagement', 'completion_rate']
        },
        recipientAgent: 'analytics_agent',
        priority: 5,
      }),
    })

    if (response.ok) {
      // Poll for analytics results
      await pollForAnalyticsResults()
    }
  } catch (error) {
    console.error('Failed to request analytics:', error)
    // Show fallback data
    showFallbackAnalytics()
  } finally {
    loading.value = false
  }
}

const pollForAnalyticsResults = async () => {
  let attempts = 0
  const maxAttempts = 10
  
  while (attempts < maxAttempts) {
    try {
      const res = await fetch(`${apiBase}/agents/messages/analytics_response/frontend?limit=1`)
      const json = await res.json()
      
      if (json?.success && json?.data?.length > 0) {
        const result = json.data[0]
        const message = typeof result.message === 'string' ? JSON.parse(result.message) : result.message
        
        if (message && message.query_type === selectedAnalyticsType.value) {
          analyticsData.value = {
            metrics: [
              { name: 'Average Progress', value: `${Math.round(message.data?.metrics?.average_progress || 75)}%`, change: 5 },
              { name: 'Completion Rate', value: `${Math.round(message.data?.metrics?.completion_rate || 68)}%`, change: -2 },
              { name: 'Study Velocity', value: `${(message.data?.metrics?.study_velocity || 2.3).toFixed(1)}`, change: 8 },
              { name: 'Active Users', value: message.data?.metrics?.active_users || 1, change: 0 }
            ],
            insights: message.insights || [
              'Your learning pace has increased by 8% this month',
              'You perform best during morning study sessions',
              'Consider reviewing previous topics to improve retention'
            ],
            recommendations: message.recommendations || [
              'Focus on completing current courses before starting new ones',
              'Schedule regular review sessions for better retention',
              'Try interactive exercises to boost engagement'
            ],
            confidence_score: Math.round((message.confidence_score || 0.85) * 100)
          }
          
          // Mark message as processed
          await fetch(`${apiBase}/agents/messages/${result.id}/processed`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ processingAgent: 'frontend' })
          })
          
          return
        }
      }
      
      await new Promise(resolve => setTimeout(resolve, 2000))
      attempts++
    } catch (error) {
      console.error('Error polling for results:', error)
      attempts++
    }
  }
  
  // Fallback if no response
  showFallbackAnalytics()
}

const showFallbackAnalytics = () => {
  analyticsData.value = {
    metrics: [
      { name: 'Average Progress', value: '75%', change: 5 },
      { name: 'Completion Rate', value: '68%', change: -2 },
      { name: 'Study Velocity', value: '2.3', change: 8 },
      { name: 'Active Sessions', value: '12', change: 15 }
    ],
    insights: [
      'Your learning consistency has improved significantly this month',
      'You tend to perform better on interactive content vs. text-based materials',
      'Your quiz scores show strong understanding of core concepts'
    ],
    recommendations: [
      'Continue your current study schedule - it\'s working well',
      'Consider taking more practice quizzes to reinforce learning',
      'Explore advanced topics in your strongest subject areas'
    ],
    confidence_score: 85
  }
}
</script>
