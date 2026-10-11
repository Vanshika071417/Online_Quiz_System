// Pre-loaded Question Banks and Quizzes
const DEFAULT_QUIZZES = [
  {
    id: "quiz-web-dev",
    joinCode: "QZ-1001",
    teacherName: "Prof. Alan Turing",
    title: "Full Stack Web & System Architecture",
    category: "Software Engineering",
    description: "Evaluate your core knowledge of modern web protocols, asynchronous JavaScript, database transactions, and scalable architecture.",
    durationMinutes: 10,
    passingScore: 70,
    tags: ["JavaScript", "HTTP", "Databases", "Architecture"],
    questions: [
      {
        id: "q1",
        text: "What will be logged to the console by the following asynchronous JavaScript execution?",
        code: `console.log('1');\nsetTimeout(() => console.log('2'), 0);\nPromise.resolve().then(() => console.log('3'));\nconsole.log('4');`,
        options: [
          "1, 2, 3, 4",
          "1, 4, 3, 2",
          "1, 4, 2, 3",
          "3, 1, 4, 2"
        ],
        correct: 1,
        explanation: "Synchronous statements ('1' and '4') run first. Then microtasks in the job queue (the resolved Promise '3') execute before macrotasks in the event loop (the setTimeout '2')."
      },
      {
        id: "q2",
        text: "In the CAP theorem of distributed systems, which combination is guaranteed by a traditional single-leader relational database system (e.g. standard PostgreSQL)?",
        code: null,
        options: [
          "Consistency and Partition Tolerance (CP)",
          "Availability and Partition Tolerance (AP)",
          "Consistency and Availability (CA) under single-partition guarantees",
          "Availability, Consistency, and Partition Tolerance simultaneously"
        ],
        correct: 2,
        explanation: "Single-node relational systems prioritize Consistency and Availability without built-in network partitioning tolerance across distributed clusters."
      },
      {
        id: "q3",
        text: "Which HTTP header is primarily used to prevent Cross-Site Scripting (XSS) attacks by restricting the origins of executable scripts?",
        code: null,
        options: [
          "Access-Control-Allow-Origin",
          "Content-Security-Policy (CSP)",
          "X-Frame-Options",
          "Strict-Transport-Security (HSTS)"
        ],
        correct: 1,
        explanation: "Content-Security-Policy (CSP) allows server operators to restrict where executable scripts, stylesheets, and images can be fetched and loaded."
      },
      {
        id: "q4",
        text: "In RESTful API design, which HTTP method should be idempotent and used to completely replace an existing resource?",
        code: null,
        options: [
          "POST",
          "PATCH",
          "PUT",
          "UPDATE"
        ],
        correct: 2,
        explanation: "PUT is idempotent and replaces the entire target resource with the uploaded payload, whereas PATCH applies partial modifications."
      },
      {
        id: "q5",
        text: "What is the primary benefit of using a Reverse Proxy (such as Nginx or Envoy) in front of application backends?",
        code: null,
        options: [
          "SSL termination, centralized load balancing, and DDoS mitigation",
          "Directly compiling client-side JavaScript into machine code",
          "Replacing the relational database for persistent disk storage",
          "Eliminating the need for CSS responsive media queries"
        ],
        correct: 0,
        explanation: "Reverse proxies manage SSL/TLS offloading, request routing/load balancing, caching, and shielding origin services."
      }
    ]
  },
  {
    id: "quiz-dsa",
    joinCode: "QZ-2002",
    teacherName: "Prof. Alan Turing",
    title: "Data Structures & Algorithmic Complexity",
    category: "Computer Science",
    description: "Benchmark your understanding of Big-O notations, binary search trees, hash table collisions, and graph traversal algorithms.",
    durationMinutes: 8,
    passingScore: 60,
    tags: ["Algorithms", "Trees", "Big-O", "HashMaps"],
    questions: [
      {
        id: "dsa-q1",
        text: "What is the worst-case time complexity of searching for an element in an unbalanced Binary Search Tree (BST) with N nodes?",
        code: null,
        options: [
          "O(1)",
          "O(log N)",
          "O(N)",
          "O(N log N)"
        ],
        correct: 2,
        explanation: "In the worst case, an unbalanced BST degenerates into a linear linked list (skewed tree), causing lookup complexity to degrade to O(N)."
      },
      {
        id: "dsa-q2",
        text: "Which traversal strategy on a Binary Search Tree (BST) visits nodes in strictly ascending numerical order?",
        code: null,
        options: [
          "Pre-order Traversal (Root, Left, Right)",
          "In-order Traversal (Left, Root, Right)",
          "Post-order Traversal (Left, Right, Root)",
          "Level-order Traversal (Breadth-First)"
        ],
        correct: 1,
        explanation: "An In-order traversal visits the left subtree first, then the current node, then the right subtree, producing sorted output."
      },
      {
        id: "dsa-q3",
        text: "Which collision resolution technique in Hash Tables uses a linked list or secondary tree at each hash bucket?",
        code: null,
        options: [
          "Separate Chaining",
          "Linear Probing",
          "Double Hashing",
          "Quadratic Probing"
        ],
        correct: 0,
        explanation: "Separate Chaining stores multiple elements colliding on the same hash bucket inside a linked list or balanced red-black tree."
      },
      {
        id: "dsa-q4",
        text: "Which algorithm finds the single-source shortest path in a weighted graph with non-negative edge weights in O(E + V log V) time with a Fibonacci heap?",
        code: null,
        options: [
          "Bellman-Ford Algorithm",
          "Floyd-Warshall Algorithm",
          "Dijkstra's Algorithm",
          "Kruskal's Algorithm"
        ],
        correct: 2,
        explanation: "Dijkstra's algorithm computes single-source shortest paths on graphs with non-negative edge weights efficiently using a priority queue."
      }
    ]
  }
];
