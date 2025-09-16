<template>
  <div class="min-h-screen bg-gray-50">
    <header class="bg-white shadow">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between py-4">
          <div class="flex items-center">
            <NuxtLink :to="`/courses/${courseId}`" class="text-gray-400 hover:text-gray-600 mr-4">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
              </svg>
            </NuxtLink>
            <div>
              <h1 class="text-xl font-bold text-gray-900">{{ currentLesson?.title || 'Loading...' }}</h1>
              <p class="text-sm text-gray-500">{{ currentCourse?.title }}</p>
            </div>
          </div>
          <div class="flex items-center space-x-4">
            <NuxtLink to="/chat" class="inline-flex items-center px-3 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50">
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-3.582 8-8 8a8.955 8.955 0 01-4.126-.98L3 20l1.98-5.874A8.955 8.955 0 013 12c0-4.418 3.582-8 8-8s8 3.582 8 8z"></path>
              </svg>
              Ask AI Tutor
            </NuxtLink>
            <button 
              @click="markComplete"
              :disabled="isCompleted"
              class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {{ isCompleted ? 'Completed' : 'Mark Complete' }}
            </button>
          </div>
        </div>
      </div>
    </header>

    <main class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Loading State -->
      <div v-if="loading" class="flex justify-center items-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-md p-4">
        <div class="flex">
          <svg class="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"></path>
          </svg>
          <div class="ml-3">
            <h3 class="text-sm font-medium text-red-800">Error loading lesson</h3>
            <p class="mt-1 text-sm text-red-700">{{ error }}</p>
          </div>
        </div>
      </div>

      <!-- Lesson Content -->
      <div v-else-if="currentLesson" class="space-y-8">
        <!-- Lesson Header -->
        <div class="bg-white shadow rounded-lg p-6">
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center">
              <span class="flex-shrink-0 w-10 h-10 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-lg font-medium mr-4">
                {{ currentLesson.lesson_order }}
              </span>
              <div>
                <h2 class="text-2xl font-bold text-gray-900">{{ currentLesson.title }}</h2>
                <div class="flex items-center text-sm text-gray-500 mt-1">
                  <span class="capitalize">{{ currentLesson.lesson_type }}</span>
                  <span class="mx-2">•</span>
                  <span>{{ currentLesson.duration }} minutes</span>
                </div>
              </div>
            </div>
            <div class="text-right">
              <div class="text-sm text-gray-500">Progress</div>
              <div class="text-2xl font-bold text-blue-600">{{ Math.round(progress) }}%</div>
            </div>
          </div>
          
          <div class="w-full bg-gray-200 rounded-full h-2">
            <div class="bg-blue-600 h-2 rounded-full transition-all duration-300" 
                 :style="{ width: `${progress}%` }"></div>
          </div>
        </div>

        <!-- Lesson Content -->
        <div class="bg-white shadow rounded-lg p-6">
          <div class="prose max-w-none">
            <div v-if="currentLesson.lesson_type === 'video'" class="mb-6">
              <div class="bg-gray-100 rounded-lg p-8 text-center">
                <svg class="mx-auto h-16 w-16 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1m4 0h1m-6 4h8m2-10v18a2 2 0 01-2 2H6a2 2 0 01-2-2V4a2 2 0 012-2h12a2 2 0 012 2z"></path>
                </svg>
                <h3 class="text-lg font-medium text-gray-900 mb-2">Video Lesson</h3>
                <p class="text-gray-600">Video player would be embedded here</p>
              </div>
            </div>

            <div v-if="currentLesson.lesson_type === 'interactive'" class="mb-6">
              <div class="bg-blue-50 border border-blue-200 rounded-lg p-6">
                <div class="flex items-center mb-4">
                  <svg class="w-6 h-6 text-blue-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-3.582 8-8 8a8.955 8.955 0 01-4.126-.98L3 20l1.98-5.874A8.955 8.955 0 013 12c0-4.418 3.582-8 8-8s8 3.582 8 8z"></path>
                  </svg>
                  <h3 class="text-lg font-medium text-blue-900">Interactive Lesson</h3>
                </div>
                <p class="text-blue-800 mb-4">This lesson includes hands-on activities. Use the AI Tutor chat to get guidance and ask questions!</p>
                <NuxtLink to="/chat" class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700">
                  Open AI Tutor Chat
                </NuxtLink>
              </div>
            </div>

            <div v-if="currentLesson.lesson_type === 'quiz'" class="mb-6">
              <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
                <div class="flex items-center mb-4">
                  <svg class="w-6 h-6 text-yellow-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                  <h3 class="text-lg font-medium text-yellow-900">Quiz Assessment</h3>
                </div>
                <p class="text-yellow-800 mb-4">This lesson includes a quiz to test your understanding of the material.</p>
                <button class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-yellow-600 hover:bg-yellow-700">
                  Start Quiz
                </button>
              </div>
            </div>

            <div class="text-gray-700 leading-relaxed">
              <p>{{ currentLesson.content }}</p>
            </div>
          </div>
        </div>

        <!-- Navigation -->
        <div class="bg-white shadow rounded-lg p-6">
          <div class="flex items-center justify-between">
            <button 
              @click="goToPrevious"
              :disabled="!previousLesson"
              class="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
              </svg>
              Previous Lesson
            </button>

            <div class="text-center">
              <p class="text-sm text-gray-500">
                Lesson {{ currentLesson.lesson_order }} of {{ totalLessons }}
              </p>
            </div>

            <button 
              @click="goToNext"
              :disabled="!nextLesson"
              class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next Lesson
              <svg class="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { useCourses } from '~/composables/useCourses'

const route = useRoute()
const router = useRouter()
const courseId = parseInt(route.params.id as string)
const lessonId = parseInt(route.params.lessonId as string)

const { currentCourse, lessons, loading, error, fetchCourse, fetchLessons } = useCourses()

const currentLesson = computed(() => {
  return lessons.value.find(lesson => lesson.id === lessonId)
})

const progress = ref(0)
const isCompleted = ref(false)

// Navigation helpers
const currentLessonIndex = computed(() => {
  return lessons.value.findIndex(lesson => lesson.id === lessonId)
})

const previousLesson = computed(() => {
  const prevIndex = currentLessonIndex.value - 1
  return prevIndex >= 0 ? lessons.value[prevIndex] : null
})

const nextLesson = computed(() => {
  const nextIndex = currentLessonIndex.value + 1
  return nextIndex < lessons.value.length ? lessons.value[nextIndex] : null
})

const totalLessons = computed(() => lessons.value.length)

// Fetch data on mount
onMounted(async () => {
  await fetchCourse(courseId)
  await fetchLessons(courseId)
  
  // Simulate progress tracking
  startProgressTracking()
})

const startProgressTracking = () => {
  // Simulate reading progress
  const interval = setInterval(() => {
    if (progress.value < 100) {
      progress.value += 2
    } else {
      clearInterval(interval)
    }
  }, 1000)
}

const markComplete = async () => {
  try {
    // TODO: Update progress via API when auth is implemented
    // await updateProgress('demo-user-1', lessonId, {
    //   progress_percentage: 100,
    //   completion_status: 'completed'
    // })
    
    isCompleted.value = true
    progress.value = 100
    
    // Auto-navigate to next lesson after a delay
    if (nextLesson.value) {
      setTimeout(() => {
        goToNext()
      }, 1500)
    }
  } catch (err) {
    console.error('Failed to mark lesson complete:', err)
  }
}

const goToPrevious = () => {
  if (previousLesson.value) {
    router.push(`/courses/${courseId}/lessons/${previousLesson.value.id}`)
  }
}

const goToNext = () => {
  if (nextLesson.value) {
    router.push(`/courses/${courseId}/lessons/${nextLesson.value.id}`)
  } else {
    // Return to course overview when finished
    router.push(`/courses/${courseId}`)
  }
}
</script>
