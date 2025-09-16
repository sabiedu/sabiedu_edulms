<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <!-- Hero Section -->
      <div class="text-center mb-16">
        <h1 class="text-4xl font-bold text-gray-900 sm:text-5xl md:text-6xl">
          EduLMS v2
        </h1>
        <p class="mt-3 max-w-md mx-auto text-base text-gray-500 sm:text-lg md:mt-5 md:text-xl md:max-w-3xl">
          AI-Powered Learning Management System with Multi-Agent Intelligence
        </p>
        <div class="mt-5 max-w-md mx-auto sm:flex sm:justify-center md:mt-8">
          <div class="rounded-md shadow">
            <NuxtLink to="/courses" class="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 md:py-4 md:text-lg md:px-10">
              Browse Courses
            </NuxtLink>
          </div>
          <div class="mt-3 rounded-md shadow sm:mt-0 sm:ml-3">
            <NuxtLink to="/chat" class="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-blue-600 bg-white hover:bg-gray-50 md:py-4 md:text-lg md:px-10">
              AI Tutor Chat
            </NuxtLink>
          </div>
        </div>
      </div>

      <!-- Features Grid -->
      <div class="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
        <!-- AI-Powered Learning -->
        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="p-6">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <svg class="h-8 w-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
                </svg>
              </div>
              <div class="ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-sm font-medium text-gray-500 truncate">AI-Powered Learning</dt>
                  <dd class="text-lg font-medium text-gray-900">Intelligent Tutoring</dd>
                </dl>
              </div>
            </div>
            <div class="mt-4">
              <p class="text-sm text-gray-600">
                Get personalized guidance from our AI Tutor Agent that adapts to your learning style and pace.
              </p>
            </div>
          </div>
        </div>

        <!-- Multi-Agent System -->
        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="p-6">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <svg class="h-8 w-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
                </svg>
              </div>
              <div class="ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-sm font-medium text-gray-500 truncate">Multi-Agent System</dt>
                  <dd class="text-lg font-medium text-gray-900">Collaborative AI</dd>
                </dl>
              </div>
            </div>
            <div class="mt-4">
              <p class="text-sm text-gray-600">
                Multiple specialized AI agents work together to provide comprehensive learning support.
              </p>
            </div>
          </div>
        </div>

        <!-- Adaptive Learning -->
        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="p-6">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <svg class="h-8 w-8 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                </svg>
              </div>
              <div class="ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-sm font-medium text-gray-500 truncate">Adaptive Learning</dt>
                  <dd class="text-lg font-medium text-gray-900">Personalized Paths</dd>
                </dl>
              </div>
            </div>
            <div class="mt-4">
              <p class="text-sm text-gray-600">
                Learning paths that adapt based on your progress, strengths, and areas for improvement.
              </p>
            </div>
          </div>
        </div>

        <!-- Real-time Analytics -->
        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="p-6">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <svg class="h-8 w-8 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                </svg>
              </div>
              <div class="ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-sm font-medium text-gray-500 truncate">Real-time Analytics</dt>
                  <dd class="text-lg font-medium text-gray-900">Progress Tracking</dd>
                </dl>
              </div>
            </div>
            <div class="mt-4">
              <p class="text-sm text-gray-600">
                Comprehensive analytics and insights to track learning progress and outcomes.
              </p>
            </div>
          </div>
        </div>

        <!-- Interactive Content -->
        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="p-6">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <svg class="h-8 w-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1m4 0h1m-6 4h8m2-10v18a2 2 0 01-2 2H6a2 2 0 01-2-2V4a2 2 0 012-2h12a2 2 0 012 2z"></path>
                </svg>
              </div>
              <div class="ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-sm font-medium text-gray-500 truncate">Interactive Content</dt>
                  <dd class="text-lg font-medium text-gray-900">Engaging Lessons</dd>
                </dl>
              </div>
            </div>
            <div class="mt-4">
              <p class="text-sm text-gray-600">
                Rich, interactive content including videos, quizzes, and hands-on activities.
              </p>
            </div>
          </div>
        </div>

        <!-- TiDB Integration -->
        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="p-6">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <svg class="h-8 w-8 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s8-1.79 8-4"></path>
                </svg>
              </div>
              <div class="ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-sm font-medium text-gray-500 truncate">TiDB Integration</dt>
                  <dd class="text-lg font-medium text-gray-900">Scalable Database</dd>
                </dl>
              </div>
            </div>
            <div class="mt-4">
              <p class="text-sm text-gray-600">
                Powered by TiDB for high-performance, scalable data management and real-time analytics.
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="mt-16 bg-white shadow rounded-lg">
        <div class="px-6 py-8">
          <h2 class="text-2xl font-bold text-gray-900 text-center mb-8">Get Started</h2>
          <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <NuxtLink to="/courses" class="group relative bg-blue-50 p-6 focus-within:ring-2 focus-within:ring-inset focus-within:ring-blue-500 rounded-lg hover:bg-blue-100 transition-colors">
              <div>
                <span class="rounded-lg inline-flex p-3 bg-blue-600 text-white">
                  <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path>
                  </svg>
                </span>
              </div>
              <div class="mt-8">
                <h3 class="text-lg font-medium text-gray-900">
                  Browse Courses
                </h3>
                <p class="mt-2 text-sm text-gray-500">
                  Explore available courses and start learning
                </p>
              </div>
            </NuxtLink>

            <NuxtLink to="/chat" class="group relative bg-green-50 p-6 focus-within:ring-2 focus-within:ring-inset focus-within:ring-green-500 rounded-lg hover:bg-green-100 transition-colors">
              <div>
                <span class="rounded-lg inline-flex p-3 bg-green-600 text-white">
                  <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-3.582 8-8 8a8.955 8.955 0 01-4.126-.98L3 20l1.98-5.874A8.955 8.955 0 013 12c0-4.418 3.582-8 8-8s8 3.582 8 8z"></path>
                  </svg>
                </span>
              </div>
              <div class="mt-8">
                <h3 class="text-lg font-medium text-gray-900">
                  AI Tutor Chat
                </h3>
                <p class="mt-2 text-sm text-gray-500">
                  Get instant help from our AI tutor
                </p>
              </div>
            </NuxtLink>

            <NuxtLink to="/dashboard" class="group relative bg-purple-50 p-6 focus-within:ring-2 focus-within:ring-inset focus-within:ring-purple-500 rounded-lg hover:bg-purple-100 transition-colors">
              <div>
                <span class="rounded-lg inline-flex p-3 bg-purple-600 text-white">
                  <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                  </svg>
                </span>
              </div>
              <div class="mt-8">
                <h3 class="text-lg font-medium text-gray-900">
                  My Dashboard
                </h3>
                <p class="mt-2 text-sm text-gray-500">
                  Track your progress and achievements
                </p>
              </div>
            </NuxtLink>

            <div class="group relative bg-yellow-50 p-6 rounded-lg opacity-50">
              <div>
                <span class="rounded-lg inline-flex p-3 bg-yellow-600 text-white">
                  <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                  </svg>
                </span>
              </div>
              <div class="mt-8">
                <h3 class="text-lg font-medium text-gray-900">
                  Analytics
                </h3>
                <p class="mt-2 text-sm text-gray-500">
                  Coming soon - Learning insights
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Set page meta
useHead({
  title: 'EduLMS v2 - AI-Powered Learning Management System',
  meta: [
    { name: 'description', content: 'Advanced LMS with multi-agent AI system for personalized learning experiences' }
  ]
})
</script>
