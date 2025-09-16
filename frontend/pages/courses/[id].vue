<template>
  <div class="min-h-screen bg-gray-50">
    <header class="bg-white shadow">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between py-6">
          <div class="flex items-center">
            <NuxtLink to="/courses" class="text-gray-400 hover:text-gray-600 mr-4">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
              </svg>
            </NuxtLink>
            <div>
              <h1 class="text-2xl font-bold text-gray-900">{{ currentCourse?.title || 'Loading...' }}</h1>
              <p class="text-sm text-gray-500">Course Details</p>
            </div>
          </div>
          <NuxtLink to="/chat" class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700">
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-3.582 8-8 8a8.955 8.955 0 01-4.126-.98L3 20l1.98-5.874A8.955 8.955 0 013 12c0-4.418 3.582-8 8-8s8 3.582 8 8z"></path>
            </svg>
            Ask AI Tutor
          </NuxtLink>
        </div>
      </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
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
            <h3 class="text-sm font-medium text-red-800">Error loading course</h3>
            <p class="mt-1 text-sm text-red-700">{{ error }}</p>
          </div>
        </div>
      </div>

      <!-- Course Content -->
      <div v-else-if="currentCourse" class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Course Info -->
        <div class="lg:col-span-2">
          <div class="bg-white shadow rounded-lg p-6 mb-6">
            <h2 class="text-xl font-semibold text-gray-900 mb-4">Course Overview</h2>
            <p class="text-gray-600 mb-6">{{ currentCourse.description }}</p>
            
            <div class="grid grid-cols-2 gap-4 mb-6">
              <div>
                <dt class="text-sm font-medium text-gray-500">Difficulty</dt>
                <dd class="mt-1">
                  <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                        :class="getDifficultyColor(currentCourse.difficulty)">
                    {{ currentCourse.difficulty }}
                  </span>
                </dd>
              </div>
              <div>
                <dt class="text-sm font-medium text-gray-500">Duration</dt>
                <dd class="mt-1 text-sm text-gray-900">{{ currentCourse.duration }} minutes</dd>
              </div>
            </div>

            <div v-if="currentCourse.learning_objectives?.length" class="mb-6">
              <h3 class="text-sm font-medium text-gray-900 mb-2">Learning Objectives</h3>
              <ul class="list-disc list-inside text-sm text-gray-600 space-y-1">
                <li v-for="objective in currentCourse.learning_objectives" :key="objective">
                  {{ objective }}
                </li>
              </ul>
            </div>

            <div v-if="currentCourse.prerequisites?.length" class="mb-6">
              <h3 class="text-sm font-medium text-gray-900 mb-2">Prerequisites</h3>
              <ul class="list-disc list-inside text-sm text-gray-600 space-y-1">
                <li v-for="prereq in currentCourse.prerequisites" :key="prereq">
                  {{ prereq }}
                </li>
              </ul>
            </div>
          </div>

          <!-- Lessons List -->
          <div class="bg-white shadow rounded-lg p-6">
            <h2 class="text-xl font-semibold text-gray-900 mb-4">Course Lessons</h2>
            
            <div v-if="lessons.length === 0" class="text-center py-8">
              <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path>
              </svg>
              <h3 class="mt-2 text-sm font-medium text-gray-900">No lessons available</h3>
              <p class="mt-1 text-sm text-gray-500">Lessons will appear here once they're added to the course.</p>
            </div>

            <div v-else class="space-y-4">
              <div
                v-for="lesson in lessons"
                :key="lesson.id"
                class="border border-gray-200 rounded-lg p-4 hover:border-gray-300 transition-colors"
              >
                <div class="flex items-center justify-between">
                  <div class="flex-1">
                    <div class="flex items-center">
                      <span class="flex-shrink-0 w-8 h-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-medium mr-3">
                        {{ lesson.lesson_order }}
                      </span>
                      <div>
                        <h3 class="text-sm font-medium text-gray-900">{{ lesson.title }}</h3>
                        <p class="text-sm text-gray-500 mt-1">{{ lesson.lesson_type }} • {{ lesson.duration }}min</p>
                      </div>
                    </div>
                    <p class="text-sm text-gray-600 mt-2 ml-11">{{ lesson.content.substring(0, 150) }}...</p>
                  </div>
                  <NuxtLink 
                    :to="`/courses/${currentCourse.id}/lessons/${lesson.id}`"
                    class="ml-4 inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-blue-700 bg-blue-100 hover:bg-blue-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                  >
                    Start
                  </NuxtLink>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Sidebar -->
        <div class="lg:col-span-1">
          <div class="bg-white shadow rounded-lg p-6 sticky top-8">
            <h3 class="text-lg font-medium text-gray-900 mb-4">Course Progress</h3>
            
            <div class="mb-6">
              <div class="flex justify-between text-sm text-gray-600 mb-1">
                <span>Overall Progress</span>
                <span>{{ Math.round(overallProgress) }}%</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div class="bg-blue-600 h-2 rounded-full transition-all duration-300" 
                     :style="{ width: `${overallProgress}%` }"></div>
              </div>
            </div>

            <div class="space-y-3">
              <div class="flex justify-between text-sm">
                <span class="text-gray-600">Lessons Completed</span>
                <span class="font-medium">{{ completedLessons }}/{{ lessons.length }}</span>
              </div>
              <div class="flex justify-between text-sm">
                <span class="text-gray-600">Time Spent</span>
                <span class="font-medium">{{ totalTimeSpent }}min</span>
              </div>
            </div>

            <div class="mt-6 pt-6 border-t border-gray-200">
              <button 
                @click="startNextLesson"
                :disabled="!nextLesson"
                class="w-full inline-flex justify-center items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {{ nextLesson ? `Continue: ${nextLesson.title}` : 'Course Complete!' }}
              </button>
            </div>
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

const { currentCourse, lessons, userProgress, loading, error, fetchCourse, fetchLessons, fetchUserProgress } = useCourses()

// Fetch course data on mount
onMounted(async () => {
  await fetchCourse(courseId)
  await fetchLessons(courseId)
  // TODO: Fetch user progress when auth is implemented
  // await fetchUserProgress('demo-user-1', courseId)
})

const getDifficultyColor = (difficulty: string) => {
  switch (difficulty?.toLowerCase()) {
    case 'beginner':
      return 'bg-green-100 text-green-800'
    case 'intermediate':
      return 'bg-yellow-100 text-yellow-800'
    case 'advanced':
      return 'bg-red-100 text-red-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

// Progress calculations (mock data for now)
const overallProgress = computed(() => {
  if (lessons.value.length === 0) return 0
  // Mock: assume 20% progress for demo
  return 20
})

const completedLessons = computed(() => {
  // Mock: assume 1 lesson completed for demo
  return Math.min(1, lessons.value.length)
})

const totalTimeSpent = computed(() => {
  // Mock: assume 10 minutes spent for demo
  return 10
})

const nextLesson = computed(() => {
  // Return first lesson for demo
  return lessons.value.length > 0 ? lessons.value[0] : null
})

const startNextLesson = () => {
  if (nextLesson.value) {
    router.push(`/courses/${courseId}/lessons/${nextLesson.value.id}`)
  }
}
</script>
