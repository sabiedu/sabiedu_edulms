<template>
  <div class="min-h-screen bg-gray-50">
    <header class="bg-white shadow">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center py-6">
          <div>
            <h1 class="text-3xl font-bold text-gray-900">Assessments & Quizzes</h1>
            <p class="mt-1 text-sm text-gray-500">AI-powered assessment creation and grading</p>
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
      <!-- Assessment Actions -->
      <div class="bg-white shadow rounded-lg p-6 mb-8">
        <h2 class="text-lg font-medium text-gray-900 mb-4">Assessment Tools</h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button @click="showCreateQuiz = true" 
                  class="flex items-center justify-center px-4 py-3 border border-gray-300 rounded-md hover:bg-gray-50">
            <svg class="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
            </svg>
            Create AI Quiz
          </button>
          
          <button @click="showGradeAssignment = true"
                  class="flex items-center justify-center px-4 py-3 border border-gray-300 rounded-md hover:bg-gray-50">
            <svg class="w-5 h-5 mr-2 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            Grade Assignment
          </button>
          
          <button @click="showFeedbackGenerator = true"
                  class="flex items-center justify-center px-4 py-3 border border-gray-300 rounded-md hover:bg-gray-50">
            <svg class="w-5 h-5 mr-2 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z"></path>
            </svg>
            Generate Feedback
          </button>
        </div>
      </div>

      <!-- Create Quiz Modal -->
      <div v-if="showCreateQuiz" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
        <div class="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
          <div class="mt-3">
            <h3 class="text-lg font-medium text-gray-900 mb-4">Create AI-Generated Quiz</h3>
            
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Lesson Content</label>
                <textarea v-model="quizContent" rows="6" 
                         class="w-full border border-gray-300 rounded-md px-3 py-2"
                         placeholder="Paste or enter the lesson content here..."></textarea>
              </div>
              
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Difficulty</label>
                  <select v-model="quizDifficulty" class="w-full border border-gray-300 rounded-md px-3 py-2">
                    <option value="beginner">Beginner</option>
                    <option value="intermediate">Intermediate</option>
                    <option value="advanced">Advanced</option>
                  </select>
                </div>
                
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Number of Questions</label>
                  <select v-model="quizQuestions" class="w-full border border-gray-300 rounded-md px-3 py-2">
                    <option value="3">3 Questions</option>
                    <option value="5">5 Questions</option>
                    <option value="10">10 Questions</option>
                  </select>
                </div>
              </div>
            </div>
            
            <div class="flex justify-end space-x-3 mt-6">
              <button @click="showCreateQuiz = false" 
                      class="px-4 py-2 text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50">
                Cancel
              </button>
              <button @click="generateQuiz" :disabled="creatingQuiz || !quizContent.trim()"
                      class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50">
                {{ creatingQuiz ? 'Generating...' : 'Generate Quiz' }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Generated Quiz Display -->
      <div v-if="generatedQuiz" class="bg-white shadow rounded-lg p-6 mb-8">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Generated Quiz</h3>
        
        <div class="space-y-6">
          <div v-for="(question, index) in generatedQuiz.questions" :key="question.id" 
               class="border border-gray-200 rounded-lg p-4">
            <h4 class="font-medium text-gray-900 mb-3">{{ index + 1 }}. {{ question.prompt }}</h4>
            
            <div v-if="question.type === 'mcq'" class="space-y-2">
              <div v-for="(option, optIndex) in question.options" :key="optIndex" 
                   class="flex items-center">
                <input type="radio" :name="`q${question.id}`" :value="optIndex" 
                       class="mr-2" :checked="optIndex === question.answer">
                <label class="text-gray-700">{{ option }}</label>
                <span v-if="optIndex === question.answer" class="ml-2 text-green-600 text-sm">(Correct)</span>
              </div>
            </div>
            
            <div v-else-if="question.type === 'short'" class="mt-2">
              <input type="text" class="w-full border border-gray-300 rounded-md px-3 py-2" 
                     placeholder="Short answer expected...">
              <p class="text-sm text-gray-500 mt-1">Expected: {{ question.answer }}</p>
            </div>
          </div>
        </div>
        
        <div class="mt-6 flex justify-end">
          <button @click="saveQuiz" class="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700">
            Save Quiz
          </button>
        </div>
      </div>

      <!-- Recent Assessments -->
      <div class="bg-white shadow rounded-lg p-6">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Recent Assessments</h3>
        
        <div class="space-y-4">
          <div v-for="assessment in recentAssessments" :key="assessment.id" 
               class="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
            <div>
              <h4 class="font-medium text-gray-900">{{ assessment.title }}</h4>
              <p class="text-sm text-gray-500">{{ assessment.type }} • {{ assessment.date }}</p>
            </div>
            <div class="text-right">
              <div class="text-lg font-medium text-gray-900">{{ assessment.score }}%</div>
              <div class="text-sm text-gray-500">{{ assessment.status }}</div>
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

// Quiz creation
const showCreateQuiz = ref(false)
const quizContent = ref('')
const quizDifficulty = ref('intermediate')
const quizQuestions = ref('5')
const creatingQuiz = ref(false)
const generatedQuiz = ref(null)

// Assignment grading
const showGradeAssignment = ref(false)
const showFeedbackGenerator = ref(false)

// Recent assessments (mock data)
const recentAssessments = ref([
  {
    id: 1,
    title: 'AI Fundamentals Quiz',
    type: 'Quiz',
    date: '2 days ago',
    score: 87,
    status: 'Completed'
  },
  {
    id: 2,
    title: 'Python Programming Assignment',
    type: 'Assignment',
    date: '1 week ago',
    score: 92,
    status: 'Graded'
  }
])

const generateQuiz = async () => {
  creatingQuiz.value = true
  
  try {
    const response = await fetch(`${apiBase}/agents/messages`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        channel: 'assessment',
        senderAgent: 'frontend',
        message: {
          task_type: 'create_quiz',
          lesson_content: quizContent.value,
          difficulty: quizDifficulty.value,
          num_questions: parseInt(quizQuestions.value)
        }
      })
    })
    
    const data = await response.json()
    
    if (data.success) {
      generatedQuiz.value = data.quiz
    } else {
      throw new Error(data.error || 'Quiz generation failed')
    }
  } catch (error) {
    console.error('Quiz generation failed:', error)
    alert('Quiz generation failed: ' + error.message)
  } finally {
    creatingQuiz.value = false
    showCreateQuiz.value = false
  }
}

const saveQuiz = () => {
  alert('Quiz saved successfully!')
  generatedQuiz.value = null
}
</script>
