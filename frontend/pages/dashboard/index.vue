<template>
  <div class="min-h-screen bg-gray-50">
    <header class="bg-white shadow">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center py-6">
          <div>
            <h1 class="text-3xl font-bold text-gray-900">Dashboard</h1>
            <p class="mt-1 text-sm text-gray-500">Track your learning progress and achievements</p>
          </div>
          <div class="flex items-center space-x-4">
            <NuxtLink to="/chat" class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700">
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-3.582 8-8 8a8.955 8.955 0 01-4.126-.98L3 20l1.98-5.874A8.955 8.955 0 013 12c0-4.418 3.582-8 8-8s8 3.582 8 8z"></path>
              </svg>
              AI Tutor
            </NuxtLink>
            <button @click="logout" class="text-gray-500 hover:text-gray-700">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Welcome Section -->
      <div class="bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg shadow-lg p-6 text-white mb-8">
        <h2 class="text-2xl font-bold mb-2">Welcome back, {{ user?.username || 'Student' }}!</h2>
        <p class="text-blue-100">Continue your learning journey with AI-powered guidance</p>
      </div>

      <!-- Stats Overview -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <svg class="h-8 w-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path>
                </svg>
              </div>
              <div class="ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-sm font-medium text-gray-500 truncate">Courses Enrolled</dt>
                  <dd class="text-lg font-medium text-gray-900">{{ stats.coursesEnrolled }}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <svg class="h-8 w-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
              </div>
              <div class="ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-sm font-medium text-gray-500 truncate">Lessons Completed</dt>
                  <dd class="text-lg font-medium text-gray-900">{{ stats.lessonsCompleted }}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <svg class="h-8 w-8 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
              </div>
              <div class="ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-sm font-medium text-gray-500 truncate">Study Time</dt>
                  <dd class="text-lg font-medium text-gray-900">{{ stats.studyTime }}h</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <svg class="h-8 w-8 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                </svg>
              </div>
              <div class="ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-sm font-medium text-gray-500 truncate">Average Score</dt>
                  <dd class="text-lg font-medium text-gray-900">{{ stats.averageScore }}%</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Current Progress & Recommendations -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        <!-- Current Progress -->
        <div class="bg-white shadow rounded-lg p-6">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Current Progress</h3>
          <div class="space-y-4">
            <div v-for="course in currentCourses" :key="course.id" class="border border-gray-200 rounded-lg p-4">
              <div class="flex items-center justify-between mb-2">
                <h4 class="text-sm font-medium text-gray-900">{{ course.title }}</h4>
                <span class="text-sm text-gray-500">{{ course.progress }}%</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div class="bg-blue-600 h-2 rounded-full transition-all duration-300" 
                     :style="{ width: `${course.progress}%` }"></div>
              </div>
              <div class="mt-2 flex justify-between text-xs text-gray-500">
                <span>{{ course.completedLessons }}/{{ course.totalLessons }} lessons</span>
                <NuxtLink :to="`/courses/${course.id}`" class="text-blue-600 hover:text-blue-500">Continue →</NuxtLink>
              </div>
            </div>
          </div>
        </div>

        <!-- AI Recommendations -->
        <div class="bg-white shadow rounded-lg p-6">
          <h3 class="text-lg font-medium text-gray-900 mb-4">AI Recommendations</h3>
          <div class="space-y-4">
            <div v-for="recommendation in recommendations" :key="recommendation.id" class="border-l-4 border-blue-500 pl-4">
              <h4 class="text-sm font-medium text-gray-900">{{ recommendation.title }}</h4>
              <p class="text-sm text-gray-600 mt-1">{{ recommendation.description }}</p>
              <div class="mt-2">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                  {{ recommendation.type }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Recent Activity -->
      <div class="bg-white shadow rounded-lg p-6 mb-8">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Recent Activity</h3>
        <div class="flow-root">
          <ul class="-mb-8">
            <li v-for="(activity, index) in recentActivity" :key="activity.id">
              <div class="relative pb-8" :class="{ 'pb-0': index === recentActivity.length - 1 }">
                <span v-if="index !== recentActivity.length - 1" class="absolute top-4 left-4 -ml-px h-full w-0.5 bg-gray-200"></span>
                <div class="relative flex space-x-3">
                  <div>
                    <span class="h-8 w-8 rounded-full flex items-center justify-center ring-8 ring-white"
                          :class="getActivityIconClass(activity.type)">
                      <svg class="h-5 w-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                        <path v-if="activity.type === 'lesson'" fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
                        <path v-else-if="activity.type === 'quiz'" fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 8a3.001 3.001 0 01-2 2.83V11a1 1 0 11-2 0v-1a1 1 0 011-1 1 1 0 100-2zm0 8a1 1 0 100-2 1 1 0 000 2z" clip-rule="evenodd"></path>
                        <path v-else fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-11a1 1 0 10-2 0v2H7a1 1 0 100 2h2v2a1 1 0 102 0v-2h2a1 1 0 100-2h-2V7z" clip-rule="evenodd"></path>
                      </svg>
                    </span>
                  </div>
                  <div class="min-w-0 flex-1 pt-1.5 flex justify-between space-x-4">
                    <div>
                      <p class="text-sm text-gray-500">{{ activity.description }}</p>
                    </div>
                    <div class="text-right text-sm whitespace-nowrap text-gray-500">
                      {{ formatTime(activity.timestamp) }}
                    </div>
                  </div>
                </div>
              </div>
            </li>
          </ul>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="bg-white shadow rounded-lg p-6">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-4">
          <NuxtLink to="/chat" class="group relative bg-gray-50 p-6 focus-within:ring-2 focus-within:ring-inset focus-within:ring-green-500 rounded-lg hover:bg-gray-100 transition-colors">
            <div>
              <span class="rounded-lg inline-flex p-3 bg-green-600 text-white group-hover:bg-green-700">
                <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-3.582 8-8 8a8.955 8.955 0 01-4.126-.98L3 20l1.98-5.874A8.955 8.955 0 013 12c0-4.418 3.582-8 8-8s8 3.582 8 8z"></path>
                </svg>
              </span>
            </div>
            <div class="mt-8">
              <h3 class="text-lg font-medium text-gray-900">AI Tutor</h3>
              <p class="mt-2 text-sm text-gray-500">Chat with AI tutor</p>
            </div>
          </NuxtLink>

          <NuxtLink to="/analytics" class="group relative bg-gray-50 p-6 focus-within:ring-2 focus-within:ring-inset focus-within:ring-purple-500 rounded-lg hover:bg-gray-100 transition-colors">
            <div>
              <span class="rounded-lg inline-flex p-3 bg-purple-600 text-white group-hover:bg-purple-700">
                <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                </svg>
              </span>
            </div>
            <div class="mt-8">
              <h3 class="text-lg font-medium text-gray-900">Analytics</h3>
              <p class="mt-2 text-sm text-gray-500">Learning insights</p>
            </div>
          </NuxtLink>

          <NuxtLink to="/assessments" class="group relative bg-gray-50 p-6 focus-within:ring-2 focus-within:ring-inset focus-within:ring-yellow-500 rounded-lg hover:bg-gray-100 transition-colors">
            <div>
              <span class="rounded-lg inline-flex p-3 bg-yellow-600 text-white group-hover:bg-yellow-700">
                <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
              </span>
            </div>
            <div class="mt-8">
              <h3 class="text-lg font-medium text-gray-900">Assessments</h3>
              <p class="mt-2 text-sm text-gray-500">AI quizzes & grading</p>
            </div>
          </NuxtLink>

          <NuxtLink to="/research" class="group relative bg-gray-50 p-6 focus-within:ring-2 focus-within:ring-inset focus-within:ring-blue-500 rounded-lg hover:bg-gray-100 transition-colors">
            <div>
              <span class="rounded-lg inline-flex p-3 bg-blue-600 text-white group-hover:bg-blue-700">
                <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                </svg>
              </span>
            </div>
            <div class="mt-8">
              <h3 class="text-lg font-medium text-gray-900">Research</h3>
              <p class="mt-2 text-sm text-gray-500">Academic research</p>
            </div>
          </NuxtLink>

          <NuxtLink to="/workflows" class="group relative bg-gray-50 p-6 focus-within:ring-2 focus-within:ring-inset focus-within:ring-indigo-500 rounded-lg hover:bg-gray-100 transition-colors">
            <div>
              <span class="rounded-lg inline-flex p-3 bg-indigo-600 text-white group-hover:bg-indigo-700">
                <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                </svg>
              </span>
            </div>
            <div class="mt-8">
              <h3 class="text-lg font-medium text-gray-900">Workflows</h3>
              <p class="mt-2 text-sm text-gray-500">Multi-agent workflows</p>
            </div>
          </NuxtLink>

          <NuxtLink to="/courses" class="group relative bg-gray-50 p-6 focus-within:ring-2 focus-within:ring-inset focus-within:ring-gray-500 rounded-lg hover:bg-gray-100 transition-colors">
            <div>
              <span class="rounded-lg inline-flex p-3 bg-gray-600 text-white group-hover:bg-gray-700">
                <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path>
                </svg>
              </span>
            </div>
            <div class="mt-8">
              <h3 class="text-lg font-medium text-gray-900">Courses</h3>
              <p class="mt-2 text-sm text-gray-500">Browse courses</p>
            </div>
          </NuxtLink>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
// Mock user for demo
const user = ref({ username: 'Demo User' })
const router = useRouter()

const logout = () => {
  // Mock logout function
  console.log('Logout clicked')
}

// Set page meta
useHead({
  title: 'Dashboard - EduLMS v2',
  meta: [
    { name: 'description', content: 'Your personalized learning dashboard' }
  ]
})

// Mock data - in real implementation, fetch from API
const stats = reactive({
  coursesEnrolled: 3,
  lessonsCompleted: 12,
  studyTime: 24,
  averageScore: 87
})

const currentCourses = reactive([
  {
    id: 1,
    title: 'AI for Beginners: Agents and Prompting',
    progress: 60,
    completedLessons: 3,
    totalLessons: 5
  },
  {
    id: 2,
    title: 'Python Programming Fundamentals',
    progress: 25,
    completedLessons: 2,
    totalLessons: 8
  }
])

const recommendations = reactive([
  {
    id: 1,
    title: 'Continue AI Basics',
    description: 'You\'re making great progress! Complete the next lesson to maintain momentum.',
    type: 'Continue Learning'
  },
  {
    id: 2,
    title: 'Practice Prompting',
    description: 'Based on your quiz results, additional practice with prompt engineering would be beneficial.',
    type: 'Skill Building'
  },
  {
    id: 3,
    title: 'Explore Advanced Topics',
    description: 'Ready for the next challenge? Check out our intermediate AI courses.',
    type: 'Next Steps'
  }
])

const recentActivity = reactive([
  {
    id: 1,
    type: 'lesson',
    description: 'Completed "Prompting Basics" lesson',
    timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000) // 2 hours ago
  },
  {
    id: 2,
    type: 'quiz',
    description: 'Scored 85% on "LLM Fundamentals" quiz',
    timestamp: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000) // 1 day ago
  },
  {
    id: 3,
    type: 'course',
    description: 'Enrolled in "AI for Beginners" course',
    timestamp: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000) // 3 days ago
  }
])

const getActivityIconClass = (type: string) => {
  switch (type) {
    case 'lesson':
      return 'bg-green-500'
    case 'quiz':
      return 'bg-blue-500'
    case 'course':
      return 'bg-purple-500'
    default:
      return 'bg-gray-500'
  }
}

const formatTime = (timestamp: Date) => {
  const now = new Date()
  const diff = now.getTime() - timestamp.getTime()
  const hours = Math.floor(diff / (1000 * 60 * 60))
  const days = Math.floor(hours / 24)
  
  if (days > 0) {
    return `${days}d ago`
  } else if (hours > 0) {
    return `${hours}h ago`
  } else {
    return 'Just now'
  }
}

const handleLogout = async () => {
  logout()
  await router.push('/auth/login')
}
</script>
