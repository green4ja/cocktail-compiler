const routes = [
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      {
        path: '',
        component: () => import('pages/BartenderFunctionality.vue'),
      },
      // {
      //   path: 'bartender',
      //   component: () => import('pages/BartenderPage.vue'),
      // },
      // {
      //   path: 'ingredients',
      //   component: () => import('pages/IngredientsPage.vue'),
      // },
      // {
      //   path: 'discover',
      //   component: () => import('pages/DiscoverPage.vue'),
      // },
      // {
      //   path: 'troubleshooting',
      //   component: () => import('pages/TroubleshootingPage.vue'),
      // },
    ],
  },
  // Always leave this as last one,
  // but you can also remove it
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue'),
  },
]

export default routes
