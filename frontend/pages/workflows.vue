<template>
  <div class="min-h-screen bg-gray-50">
    <header class="bg-white shadow">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center py-6">
          <div>
            <h1 class="text-3xl font-bold text-gray-900">Multi-Agent Workflows</h1>
            <p class="mt-1 text-sm text-gray-500">Automated multi-step AI workflows with TiDB integration</p>
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
      <!-- Workflow Selection -->
      <div class="bg-white shadow rounded-lg p-6 mb-8">
        <h2 class="text-lg font-medium text-gray-900 mb-4">Available Workflows</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div v-for="(workflow, key) in availableWorkflows" :key="key" 
               class="border border-gray-200 rounded-lg p-4 hover:border-blue-300 cursor-pointer"
               @click="selectWorkflow(key, workflow)">
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <h3 class="text-lg font-medium text-gray-900">{{ workflow.name }}</h3>
                <p class="text-sm text-gray-500 mt-1">{{ workflow.description }}</p>
                
                <div class="mt-3">
                  <div class="text-xs text-gray-400 mb-1">Workflow Steps:</div>
                  <div class="flex flex-wrap gap-1">
                    <span v-for="step in workflow.steps" :key="step" 
                          class="inline-flex items-center px-2 py-1 rounded-full text-xs bg-blue-100 text-blue-800">
                      {{ step.replace('_', ' ') }}
                    </span>
                  </div>
                </div>
                
                <div class="mt-3">
                  <div class="text-xs text-gray-400 mb-1">Required Parameters:</div>
                  <div class="text-xs text-gray-600">
                    {{ workflow.required_params.join(', ') }}
                  </div>
                </div>
              </div>
              
              <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
              </svg>
            </div>
          </div>
        </div>
      </div>

      <!-- Workflow Configuration Modal -->
      <div v-if="selectedWorkflow" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
        <div class="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
          <div class="mt-3">
            <h3 class="text-lg font-medium text-gray-900 mb-4">Configure {{ selectedWorkflow.name }}</h3>
            
            <div class="space-y-4">
              <!-- Dynamic form fields based on workflow requirements -->
              <div v-for="param in selectedWorkflow.required_params" :key="param" class="space-y-2">
                <label class="block text-sm font-medium text-gray-700">
                  {{ formatParamName(param) }}
                  <span class="text-red-500">*</span>
                </label>
                
                <!-- User ID field -->
                <input v-if="param === 'user_id'" 
                       v-model="workflowParams[param]" 
                       type="text" 
                       class="w-full border border-gray-300 rounded-md px-3 py-2"
                       :placeholder="getParamPlaceholder(param)">
                
                <!-- Course ID field -->
                <input v-else-if="param === 'course_id'" 
                       v-model="workflowParams[param]" 
                       type="text" 
                       class="w-full border border-gray-300 rounded-md px-3 py-2"
                       :placeholder="getParamPlaceholder(param)">
                
                <!-- Topic field -->
                <input v-else-if="param === 'topic'" 
                       v-model="workflowParams[param]" 
                       type="text" 
                       class="w-full border border-gray-300 rounded-md px-3 py-2"
                       :placeholder="getParamPlaceholder(param)">
                
                <!-- Research query field -->
                <input v-else-if="param === 'research_query'" 
                       v-model="workflowParams[param]" 
                       type="text" 
                       class="w-full border border-gray-300 rounded-md px-3 py-2"
                       :placeholder="getParamPlaceholder(param)">
                
                <!-- Lesson content field -->
                <textarea v-else-if="param === 'lesson_content'" 
                          v-model="workflowParams[param]" 
                          rows="4" 
                          class="w-full border border-gray-300 rounded-md px-3 py-2"
                          :placeholder="getParamPlaceholder(param)"></textarea>
                
                <!-- Learning goals field -->
                <textarea v-else-if="param === 'learning_goals'" 
                          v-model="workflowParams[param]" 
                          rows="3" 
                          class="w-full border border-gray-300 rounded-md px-3 py-2"
                          placeholder="Enter learning goals, one per line"></textarea>
                
                <!-- Difficulty field -->
                <select v-else-if="param === 'difficulty'" 
                        v-model="workflowParams[param]" 
                        class="w-full border border-gray-300 rounded-md px-3 py-2">
                  <option value="">Select difficulty</option>
                  <option value="beginner">Beginner</option>
                  <option value="intermediate">Intermediate</option>
                  <option value="advanced">Advanced</option>
                </select>
                
                <!-- Content type field -->
                <select v-else-if="param === 'content_type'" 
                        v-model="workflowParams[param]" 
                        class="w-full border border-gray-300 rounded-md px-3 py-2">
                  <option value="">Select content type</option>
                  <option value="lesson">Lesson</option>
                  <option value="quiz">Quiz</option>
                  <option value="assignment">Assignment</option>
                  <option value="summary">Summary</option>
                </select>
                
                <!-- Default text input -->
                <input v-else 
                       v-model="workflowParams[param]" 
                       type="text" 
                       class="w-full border border-gray-300 rounded-md px-3 py-2"
                       :placeholder="getParamPlaceholder(param)">
              </div>
            </div>
            
            <div class="flex justify-end space-x-3 mt-6">
              <button @click="selectedWorkflow = null; workflowParams = {}" 
                      class="px-4 py-2 text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50">
                Cancel
              </button>
              <button @click="executeWorkflow" 
                      :disabled="executingWorkflow || !isFormValid"
                      class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50">
                {{ executingWorkflow ? 'Executing...' : 'Execute Workflow' }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Workflow Execution Progress -->
      <div v-if="currentExecution" class="bg-white shadow rounded-lg p-6 mb-8">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Workflow Execution Progress</h3>
        
        <div class="mb-4">
          <div class="flex justify-between text-sm text-gray-600 mb-1">
            <span>{{ currentExecution.workflow_name }}</span>
            <span>{{ Math.round(currentExecution.progress || 0) }}%</span>
          </div>
          <div class="w-full bg-gray-200 rounded-full h-2">
            <div class="bg-blue-600 h-2 rounded-full transition-all duration-300" 
                 :style="{ width: `${currentExecution.progress || 0}%` }"></div>
          </div>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div class="text-center">
            <div class="text-2xl font-bold text-blue-600">{{ currentExecution.current_step || 'Starting' }}</div>
            <div class="text-sm text-gray-500">Current Step</div>
          </div>
          <div class="text-center">
            <div class="text-2xl font-bold text-green-600">{{ currentExecution.completed_steps || 0 }}</div>
            <div class="text-sm text-gray-500">Completed Steps</div>
          </div>
          <div class="text-center">
            <div class="text-2xl font-bold text-gray-600">{{ currentExecution.total_steps || 5 }}</div>
            <div class="text-sm text-gray-500">Total Steps</div>
          </div>
        </div>
        
        <div v-if="currentExecution.status === 'completed'" class="bg-green-50 border border-green-200 rounded-lg p-4">
          <div class="flex items-center">
            <svg class="w-5 h-5 text-green-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
            </svg>
            <span class="text-green-800 font-medium">Workflow completed successfully!</span>
          </div>
        </div>
      </div>

      <!-- Workflow Results -->
      <div v-if="workflowResults" class="bg-white shadow rounded-lg p-6 mb-8">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Workflow Results</h3>
        
        <div class="space-y-4">
          <div v-for="(result, stepName) in workflowResults.task_results" :key="stepName" 
               class="border border-gray-200 rounded-lg p-4">
            <h4 class="font-medium text-gray-900 mb-2">{{ formatStepName(stepName) }}</h4>
            
            <div class="bg-gray-50 rounded-lg p-3">
              <pre class="text-sm text-gray-700 whitespace-pre-wrap">{{ formatResult(result) }}</pre>
            </div>
          </div>
        </div>
        
        <div class="mt-6 flex justify-end">
          <button @click="downloadResults" 
                  class="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700">
            Download Results
          </button>
        </div>
      </div>

      <!-- Workflow History -->
      <div class="bg-white shadow rounded-lg p-6">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Recent Workflows</h3>
        
        <div class="space-y-4">
          <div v-for="workflow in workflowHistory" :key="workflow.workflow_id" 
               class="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
            <div>
              <h4 class="font-medium text-gray-900">{{ formatWorkflowName(workflow.workflow_name) }}</h4>
              <p class="text-sm text-gray-500">{{ formatDate(workflow.started_at) }}</p>
            </div>
            <div class="text-right">
              <div class="flex items-center space-x-2">
                <span :class="getStatusClass(workflow.status)" 
                      class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium">
                  {{ workflow.status }}
                </span>
                <span class="text-sm text-gray-500">{{ workflow.success_rate }}%</span>
              </div>
            </div>
          </div>
        </div>
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

// Reactive data
const availableWorkflows = ref({})
const selectedWorkflow = ref(null)
const workflowParams = ref({})
const executingWorkflow = ref(false)
const currentExecution = ref(null)
const workflowResults = ref(null)
const workflowHistory = ref([])

// Computed properties
const isFormValid = computed(() => {
  if (!selectedWorkflow.value) return false
  
  return selectedWorkflow.value.required_params.every(param => {
    const value = workflowParams.value[param]
    return value && value.toString().trim().length > 0
  })
})

// Load available workflows on mount
onMounted(async () => {
  await loadAvailableWorkflows()
  await loadWorkflowHistory()
})

// Methods
const loadAvailableWorkflows = async () => {
  try {
    const response = await fetch(`${apiBase}/workflows/available`)
    const data = await response.json()
    
    if (data.success) {
      availableWorkflows.value = data.data
    }
  } catch (error) {
    console.error('Failed to load workflows:', error)
  }
}

const selectWorkflow = (key: string, workflow: any) => {
  selectedWorkflow.value = { ...workflow, key }
  workflowParams.value = {}
  
  // Pre-fill user_id if available
  if (workflow.required_params.includes('user_id') && user.value?.id) {
    workflowParams.value.user_id = user.value.id
  }
}

const executeWorkflow = async () => {
  if (!selectedWorkflow.value || !isFormValid.value) return
  
  executingWorkflow.value = true
  
  try {
    // Process learning goals if it's an array field
    const processedParams = { ...workflowParams.value }
    if (processedParams.learning_goals && typeof processedParams.learning_goals === 'string') {
      processedParams.learning_goals = processedParams.learning_goals
        .split('\n')
        .map(goal => goal.trim())
        .filter(goal => goal.length > 0)
    }
    
    const response = await fetch(`${apiBase}/workflows/execute`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        workflow_name: selectedWorkflow.value.key,
        initial_data: processedParams,
        user_id: user.value?.id
      })
    })
    
    const data = await response.json()
    
    if (data.success) {
      workflowResults.value = data.data
      currentExecution.value = {
        workflow_name: selectedWorkflow.value.name,
        status: 'completed',
        progress: 100,
        current_step: 'completed',
        completed_steps: selectedWorkflow.value.steps.length,
        total_steps: selectedWorkflow.value.steps.length
      }
      
      // Refresh history
      await loadWorkflowHistory()
    } else {
      throw new Error(data.error || 'Workflow execution failed')
    }
  } catch (error) {
    console.error('Workflow execution failed:', error)
    alert('Workflow execution failed: ' + error.message)
  } finally {
    executingWorkflow.value = false
    selectedWorkflow.value = null
    workflowParams.value = {}
  }
}

const loadWorkflowHistory = async () => {
  try {
    const response = await fetch(`${apiBase}/workflows/history?user_id=${user.value?.id || ''}&limit=10`)
    const data = await response.json()
    
    if (data.success) {
      workflowHistory.value = data.data.workflows
    }
  } catch (error) {
    console.error('Failed to load workflow history:', error)
  }
}

const downloadResults = () => {
  if (!workflowResults.value) return
  
  const dataStr = JSON.stringify(workflowResults.value, null, 2)
  const dataBlob = new Blob([dataStr], { type: 'application/json' })
  const url = URL.createObjectURL(dataBlob)
  
  const link = document.createElement('a')
  link.href = url
  link.download = `workflow_results_${workflowResults.value.workflow_id}.json`
  link.click()
  
  URL.revokeObjectURL(url)
}

// Utility functions
const formatParamName = (param: string) => {
  return param.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const getParamPlaceholder = (param: string) => {
  const placeholders = {
    user_id: 'Enter user ID',
    course_id: 'Enter course ID',
    topic: 'Enter topic or subject',
    research_query: 'Enter research question or topic',
    lesson_content: 'Paste lesson content here...',
    learning_goals: 'Enter learning goals, one per line'
  }
  return placeholders[param] || `Enter ${formatParamName(param).toLowerCase()}`
}

const formatStepName = (stepName: string) => {
  return stepName.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const formatWorkflowName = (workflowName: string) => {
  return workflowName.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const formatResult = (result: any) => {
  if (typeof result === 'object') {
    return JSON.stringify(result, null, 2)
  }
  return result?.toString() || 'No result'
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleString()
}

const getStatusClass = (status: string) => {
  const classes = {
    completed: 'bg-green-100 text-green-800',
    failed: 'bg-red-100 text-red-800',
    running: 'bg-blue-100 text-blue-800',
    pending: 'bg-yellow-100 text-yellow-800'
  }
  return classes[status] || 'bg-gray-100 text-gray-800'
}
</script>
