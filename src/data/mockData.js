export const INITIAL_USER = {
  id: "usr_anon_982",
  username: "LavenderPhoenix",
  pronouns: "they/them",
  avatarBg: "linear-gradient(135deg, #a855f7, #ec4899)",
  identityTags: ["Queer", "Non-Binary", "Ally Friendly"],
  city: "All India",
  closetPin: "1234",
  autoBlurContent: true,
  karmaScore: 428
};

export const CITIES = [
  "All India",
  "Delhi NCR",
  "Mumbai",
  "Bengaluru",
  "Kolkata",
  "Pune",
  "Hyderabad",
  "Chennai",
  "Tier 2 / Tier 3 Towns"
];

export const FEED_CATEGORIES = [
  { id: "all", label: "✨ All Posts", count: 24 },
  { id: "ComingOut", label: "🌱 #ComingOut", count: 6 },
  { id: "MentalHealth", label: "🧠 #MentalHealth", count: 8 },
  { id: "TransPride", label: "🏳️⚧️ #TransPride", count: 5 },
  { id: "Career", label: "💼 #Career", count: 4 },
  { id: "Dating", label: "💜 #Dating", count: 3 },
  { id: "LegalHelp", label: "⚖️ #LegalHelp", count: 4 },
  { id: "QueerJoy", label: "🌈 #QueerJoy", count: 7 }
];

export const INITIAL_POSTS = [
  {
    id: "post-1",
    author: "VelvetFalcon",
    pronouns: "she/they",
    avatarBg: "linear-gradient(135deg, #ec4899, #f43f5e)",
    city: "Pune",
    tags: ["ComingOut", "QueerJoy"],
    timestamp: "2 hours ago",
    title: "Came out to my elder sister last night... and she just ordered biryani 😭❤️",
    content: "I have been sweating and overthinking this for almost 3 years. My family is fairly traditional Maharashtrian. Last night while watching a movie, my heart was hammering at 150 BPM. I whispered: 'Didi, I'm gay.' She paused the movie, looked at me, hugged me tight and said: 'I know, idiot. I’ve known since you were 17. Now stop crying, let’s order chicken biryani.' For anyone feeling trapped in the closet right now, please stay safe, but know that genuine love exists.",
    contentWarning: null,
    isBlurred: false,
    upvotes: 342,
    downvotes: 4,
    userVote: 1,
    saved: true,
    commentsCount: 28,
    comments: [
      {
        id: "c-101",
        author: "CosmicStar",
        pronouns: "he/him",
        timestamp: "1 hour ago",
        text: "This brought tears to my eyes! Treasure your didi, she is a rockstar. Sending so much queer joy your way!"
      },
      {
        id: "c-102",
        author: "IndigoEcho",
        pronouns: "they/them",
        timestamp: "45 mins ago",
        text: "The biryani seal of acceptance! So happy for you friend. Take your time with the rest of the world."
      }
    ]
  },
  {
    id: "post-2",
    author: "Solaris_TG",
    pronouns: "she/her",
    avatarBg: "linear-gradient(135deg, #5bcefa, #f5a9b8)",
    city: "Delhi NCR",
    tags: ["TransPride", "LegalHelp"],
    timestamp: "4 hours ago",
    title: "Step-by-step guide: Successfully got my Transgender Identity Certificate from the National Portal!",
    content: "A lot of folks get terrified by the bureaucracy or agents asking for bribes. You DO NOT need to pay anyone. 1. Go to transgender.dosje.gov.in. 2. Upload affidavit + Aadhaar. 3. The DM office has a strict 30-day mandate. If they delay, you can file a grievance on CPGRAMS. My revised Aadhaar card is now officially updated! DM me if anyone needs the affidavit draft template.",
    contentWarning: null,
    isBlurred: false,
    upvotes: 219,
    downvotes: 1,
    userVote: 0,
    saved: false,
    commentsCount: 15,
    comments: [
      {
        id: "c-201",
        author: "Maya_Quiet",
        pronouns: "she/her",
        timestamp: "3 hours ago",
        text: "Congratulations Solaris! Please share the affidavit wording if possible, dealing with SDM in Rohini right now."
      }
    ]
  },
  {
    id: "post-3",
    author: "TechieQueer",
    pronouns: "he/him",
    avatarBg: "linear-gradient(135deg, #3b82f6, #1d4ed8)",
    city: "Bengaluru",
    tags: ["Career", "MentalHealth"],
    timestamp: "7 hours ago",
    title: "Navigating corporate DEI in Indian IT hubs: Which companies actually walk the talk?",
    content: "Wanted to share my 4-year experience across two tech giants in Outer Ring Road Bangalore. Company A had rainbow logos in June but zero health insurance for same-sex partners and HR was completely clueless about trans medical leave. Company B has comprehensive partner coverage, gender affirmation leave, and an active employee resource group. Always ask about benefits policy wording during final HR rounds!",
    contentWarning: null,
    isBlurred: false,
    upvotes: 184,
    downvotes: 3,
    userVote: 0,
    saved: false,
    commentsCount: 22,
    comments: [
      {
        id: "c-301",
        author: "ByteNomad",
        pronouns: "they/them",
        timestamp: "5 hours ago",
        text: "Preach! Pinkwashing is real in Indian corporate circles. Real inclusion is partner insurance + gender neutral restrooms."
      }
    ]
  },
  {
    id: "post-4",
    author: "SmallTownHeart",
    pronouns: "they/them",
    avatarBg: "linear-gradient(135deg, #f59e0b, #d97706)",
    city: "Tier 2 / Tier 3 Towns",
    tags: ["ComingOut", "MentalHealth"],
    timestamp: "12 hours ago",
    title: "To everyone living in small towns where there is zero queer visibility",
    content: "I am writing this from a town near Jabalpur. There are no rainbow cafes here, no pride parades, no affirming therapists within 150 km. Living in the closet 24/7 is suffocating. Finding this app and knowing you all exist is the only reason I haven't lost my sanity. If you're also in a Tier 2/3 town, you are not alone, you are not abnormal, and you have a future waiting for you.",
    contentWarning: "Contains discussion of mental exhaustion & loneliness in non-affirming environments",
    isBlurred: true,
    upvotes: 512,
    downvotes: 2,
    userVote: 0,
    saved: true,
    commentsCount: 46,
    comments: [
      {
        id: "c-401",
        author: "BhopalBirch",
        pronouns: "she/her",
        timestamp: "11 hours ago",
        text: "Sending you the biggest hug from Bhopal. We have an online book club every Sunday for MP/Central India folks. Come join us!"
      }
    ]
  },
  {
    id: "post-5",
    author: "AdvocateQueer",
    pronouns: "she/her",
    avatarBg: "linear-gradient(135deg, #10b981, #059669)",
    city: "Mumbai",
    tags: ["LegalHelp"],
    timestamp: "1 day ago",
    title: "Supreme Court Guidelines Clarification: Joint Bank Accounts & Medical Proxy for LGBTQ+ Couples",
    content: "Quick legal breakdown: Even though marriage equality was not enacted in the 2023 ruling, the Union Cabinet Committee issued official circulars allowing same-sex and queer partners to: 1. Open joint bank accounts with 'Either or Survivor' mandate. 2. Nominate partners for gratuity/provident fund. 3. Issue medical Power of Attorney for emergency healthcare decisions.",
    contentWarning: null,
    isBlurred: false,
    upvotes: 295,
    downvotes: 5,
    userVote: 0,
    saved: true,
    commentsCount: 19,
    comments: []
  }
];

export const SAFE_SPACES = [
  {
    id: "space-1",
    name: "Champaca Bookstore, Library & Cafe",
    category: "Cafe",
    city: "Bengaluru",
    neighborhood: "Edward Road / Vasanth Nagar",
    lat: 12.9856,
    lng: 77.5971,
    rating: 4.9,
    reviewsCount: 184,
    verifiedBadge: true,
    amenities: [
      "Gender-Neutral Restroom",
      "Queer Lit Shelf",
      "Discreet & Cozy",
      "Pride Flag Displayed",
      "Host of Queer Read Meets"
    ],
    contact: "+91 93536 08989",
    hours: "10:30 AM – 7:00 PM (Tue-Sun)",
    description: "An independently run, fiercely inclusive feminist and queer-welcoming cafe and sanctuary hidden amidst green foliage. Known for safe author events and poetry sessions.",
    reviews: [
      { user: "AuraBlue", rating: 5, text: "The safest, most peaceful corner in Bangalore. You can hold hands or read trans literature without anyone giving you uncomfortable stares." },
      { user: "Karan_T", rating: 5, text: "Staff is trained and respectful of pronouns. Delicious iced mocha too!" }
    ]
  },
  {
    id: "space-2",
    name: "The Humsafar Trust & Sanjeevani Clinic",
    category: "NGO",
    city: "Mumbai",
    neighborhood: "Santacruz East",
    lat: 19.0825,
    lng: 72.8428,
    rating: 4.8,
    reviewsCount: 310,
    verifiedBadge: true,
    amenities: [
      "Confidential Testing & PrEP",
      "Free Legal Aid Desk",
      "Trans Health Support",
      "Emergency Crisis Counselor",
      "Safe Drop-in Lounge"
    ],
    contact: "+91 22 2667 3800",
    hours: "10:00 AM – 6:00 PM (Mon-Fri)",
    description: "India's pioneer LGBTQ+ organization founded in 1994. Offers free and confidential HIV/STI screening, gender affirmation guidance, mental health counseling, and crisis shelters.",
    reviews: [
      { user: "Rohan_M", rating: 5, text: "Absolute lifesaver. The doctors are zero-judgment, kind, and understand sexual health nuances without lecturing." }
    ]
  },
  {
    id: "space-3",
    name: "Dr. Radhika Sen & Associates (Affirming Psychology)",
    category: "Therapist",
    city: "Delhi NCR",
    neighborhood: "Hauz Khas Enclave",
    lat: 28.5494,
    lng: 77.2001,
    rating: 5.0,
    reviewsCount: 92,
    verifiedBadge: true,
    amenities: [
      "Certified Queer-Affirmative (QACP)",
      "Gender Dysphoria WPATH Support",
      "Sliding Scale Slots for Students",
      "Online + In-Person Sessions"
    ],
    contact: "+91 98112 44321",
    hours: "11:00 AM – 8:00 PM (By Appt)",
    description: "Senior queer-affirmative clinical psychologist specializing in coming-out anxiety, family counseling, and medical gender transition documentation without conversion therapy harm.",
    reviews: [
      { user: "Zenith_9", rating: 5, text: "Dr. Sen helped me accept my identity after 10 years of self-hate. True healing sanctuary." }
    ]
  },
  {
    id: "space-4",
    name: "Sappho for Equality Resource Center",
    category: "NGO",
    city: "Kolkata",
    neighborhood: "Jadavpur",
    lat: 22.4988,
    lng: 88.3712,
    rating: 4.9,
    reviewsCount: 145,
    verifiedBadge: true,
    amenities: [
      "Lesbian / Bisexual / Trans Safe Haven",
      "Emergency Shelter Coordination",
      "Legal Cell for Stalking & Abuse",
      "Queer Film Archives"
    ],
    contact: "+91 33 2441 9995",
    hours: "11:00 AM – 6:30 PM",
    description: "Eastern India's premier activist hub dedicated to sexually marginalized women and trans persons. Safe house support and legal defense against forced marriages.",
    reviews: [
      { user: "Poulomi_K", rating: 5, text: "They literally rescued a friend from being locked up at home. Unmatched courage and dedication." }
    ]
  },
  {
    id: "space-5",
    name: "Waari Book Cafe",
    category: "Cafe",
    city: "Pune",
    neighborhood: "Kothrud",
    lat: 18.5074,
    lng: 73.8077,
    rating: 4.7,
    reviewsCount: 220,
    verifiedBadge: true,
    amenities: [
      "Quiet Working Booths",
      "Queer Friendly Staff",
      "Community Pinboard",
      "Inclusive Cultural Events"
    ],
    contact: "+91 98901 23456",
    hours: "9:00 AM – 10:00 PM",
    description: "A cultural melting pot where local Pune queer groups regularly host weekend book swaps, sketch meets, and safe meetups.",
    reviews: [
      { user: "Shantanu_P", rating: 5, text: "Very friendly crowd. You can sit with a date or work alone without feeling judged." }
    ]
  },
  {
    id: "space-6",
    name: "Mitra LGBTQ+ Youth Clinic & Wellness",
    category: "Clinic",
    city: "Hyderabad",
    neighborhood: "Banjara Hills, Road No 12",
    lat: 17.4156,
    lng: 78.4357,
    rating: 4.8,
    reviewsCount: 110,
    verifiedBadge: true,
    amenities: [
      "Affirming Physicians",
      "Discreet Billing",
      "Endocrinology Referrals",
      "Mental Health Triage"
    ],
    contact: "+91 40 2333 4455",
    hours: "10:00 AM – 7:00 PM",
    description: "Dedicated non-discriminatory general healthcare clinic tailored for LGBTQIA+ youth and working professionals in Hyderabad.",
    reviews: [
      { user: "Chaitanya_V", rating: 5, text: "They address you with correct pronouns without making a big deal out of it." }
    ]
  }
];

export const CRISIS_HELPLINES = [
  {
    name: "Tele-MANAS (Govt of India)",
    number: "14416",
    tollFree: true,
    hours: "24/7 Available",
    languages: "Hindi, English & 20 Regional Languages",
    type: "Crisis & Suicide Prevention",
    description: "Official National Tele Mental Health Programme of India. Free mental health triage and psychiatric emergency support."
  },
  {
    name: "Vandrevala Foundation Mental Health",
    number: "+91 9999 666 555",
    tollFree: false,
    hours: "24/7 Available",
    languages: "Hindi, English, Marathi, Gujarati, Tamil",
    type: "Affirming Crisis Support",
    description: "Staffed by certified psychologists trained in queer sensitivity and de-escalation for youth facing familial distress."
  },
  {
    name: "iCall Psychosocial Helpline (TISS)",
    number: "9152987821",
    tollFree: false,
    hours: "Mon – Sat (10:00 AM – 8:00 PM)",
    languages: "English, Hindi, Marathi",
    type: "Psychosocial & Relationship",
    description: "Run by Tata Institute of Social Sciences. Deeply affirmative of sexual and gender minorities."
  },
  {
    name: "Sahodari Transgender Emergency Cell",
    number: "1800 200 3802",
    tollFree: true,
    hours: "24/7 Emergency Line",
    languages: "Tamil, English, Hindi",
    type: "Transgender Safety & Abuse",
    description: "Immediate emergency response for transgender individuals facing physical violence, illegal eviction, or police harassment."
  },
  {
    name: "Naz Foundation LGBTQ+ Helpline",
    number: "+91 11 4057 0400",
    tollFree: false,
    hours: "Mon – Fri (10:00 AM – 5:30 PM)",
    languages: "Hindi, English",
    type: "Sexual Health & Coming Out",
    description: "Expert guidance on sexual health, coming out questions, and STI counseling in Northern India."
  }
];

export const THERAPISTS = [
  {
    id: "th-1",
    name: "Ananya Deshpande (she/they)",
    qualification: "M.Sc. Clinical Psychology, QACP Certified",
    experience: "8+ Years Experience",
    specialties: ["Gender Identity & Dysphoria", "Coming Out to Family", "C-PTSD & Religious Trauma"],
    languages: ["English", "Hindi", "Marathi"],
    fee: "₹1,200 – ₹1,800 / session",
    slidingScale: true,
    avatar: "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=150&auto=format&fit=crop&q=80",
    rating: 4.9,
    mode: "Online & In-Person (Mumbai)"
  },
  {
    id: "th-2",
    name: "Dr. Vikramaditya Roy (he/him)",
    qualification: "M.D. Psychiatry, LGBTQ+ Affirmative Fellow",
    experience: "12+ Years Experience",
    specialties: ["Adult ADHD in Queer Folks", "Harm-Reduction & Addiction", "Partner Counseling"],
    languages: ["English", "Hindi", "Bengali"],
    fee: "₹2,000 / session",
    slidingScale: false,
    avatar: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80",
    rating: 5.0,
    mode: "Online & In-Person (Delhi)"
  },
  {
    id: "th-3",
    name: "Samira Khan (they/she)",
    qualification: "M.A. Counseling Psychology, Narrative Therapy",
    experience: "5+ Years Experience",
    specialties: ["Non-Binary Exploration", "College Anxiety & Closeting", "Queer Body Image"],
    languages: ["English", "Hindi", "Urdu"],
    fee: "₹900 – ₹1,400 / session",
    slidingScale: true,
    avatar: "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=150&auto=format&fit=crop&q=80",
    rating: 4.8,
    mode: "Online (Pan-India)"
  }
];

export const CHAT_ROOMS = [
  {
    id: "room-1",
    name: "🌿 College & Youth Safe Space",
    tag: "College",
    members: 142,
    description: "Support for students, navigating hostel life, closet safety, and exams.",
    initialMessages: [
      { id: "m1", sender: "AsterSky", pronouns: "they/them", text: "Anyone here preparing for CAT while also dealing with conservative roommates?", time: "10:14 AM", isSensitive: false },
      { id: "m2", sender: "NeonTiger", pronouns: "he/him", text: "Yes! Hang in there friend. Keep your phone locked with a biometric code and stay strong.", time: "10:18 AM", isSensitive: false }
    ]
  },
  {
    id: "room-2",
    name: "🏳️⚧️ Trans & Non-Binary Circle",
    tag: "Trans",
    members: 89,
    description: "HRT advice, safe endocrinologists, legal name change procedures, and mutual care.",
    initialMessages: [
      { id: "m3", sender: "Zephyr_TG", pronouns: "she/her", text: "Got my first hormone consultation scheduled next Tuesday in Mumbai! Super nervous.", time: "09:30 AM", isSensitive: false },
      { id: "m4", sender: "Oakley_NB", pronouns: "they/them", text: "You're going to do great! Remember to bring a notebook to write all questions.", time: "09:35 AM", isSensitive: false }
    ]
  },
  {
    id: "room-3",
    name: "💼 Workplace & Career Pride",
    tag: "Career",
    members: 110,
    description: "Job leads at affirming MNCs, dealing with workplace harassment, and DEI networks.",
    initialMessages: [
      { id: "m5", sender: "CorpQueer", pronouns: "she/her", text: "Does anyone know if Infosys Bangalore covers gender affirmation surgery in their insurance?", time: "Yesterday", isSensitive: false },
      { id: "m6", sender: "DevLead", pronouns: "he/they", text: "Yes, they revised their policy last year up to 3 lakhs under specialized DEI care.", time: "Yesterday", isSensitive: false }
    ]
  }
];

export const LEGAL_RESOURCES = [
  {
    id: "leg-1",
    title: "Navtej Singh Johar v. Union of India (Section 377)",
    year: "2018 Landmark Judgment",
    category: "Decriminalization",
    summary: "The 5-judge Constitution bench unanimously ruled that Section 377 Indian Penal Code, insofar as it criminalized consensual homosexual acts between adults, is unconstitutional and violates Articles 14, 15, 19, and 21.",
    keyRights: [
      "Consensual same-sex intimacy in private spaces is a fundamental constitutional right.",
      "Police cannot arrest, blackmail, or detain LGBTQ+ individuals on grounds of sexual orientation.",
      "Right to privacy and spatial autonomy explicitly guaranteed under the Constitution."
    ]
  },
  {
    id: "leg-2",
    title: "Transgender Persons (Protection of Rights) Act & Rules",
    year: "2019 / 2020",
    category: "Transgender Rights",
    summary: "Provides statutory recognition of gender identity without mandatory surgical requirements for the initial Certificate of Identity.",
    keyRights: [
      "Self-perceived gender identity recognized by law through the online National Portal (transgender.dosje.gov.in).",
      "District Magistrate must issue the Identity Certificate within 30 days of application.",
      "Prohibits discrimination in education, employment, healthcare, and public facilities.",
      "Punishment prescribed for compelling trans persons into forced labor or begging."
    ]
  },
  {
    id: "leg-3",
    title: "Supriyo @ Supriya Chakraborty Ruling & Cabinet Directives",
    year: "2023–2024",
    category: "Partnership & Property Rights",
    summary: "While the Supreme Court held that the Special Marriage Act cannot be rewritten by judicial fiat, it mandated the Union Government to guarantee social and financial rights.",
    keyRights: [
      "Queer couples can legally maintain joint bank accounts ('Either or Survivor').",
      "Right to nominate same-sex partners in life insurance, employee gratuity, and EPF.",
      "Medical proxy rights: Partners are permitted in ICUs and to sign medical consent forms.",
      "Police harassment of queer consenting adults seeking shelter together is strictly barred."
    ]
  },
  {
    id: "leg-4",
    title: "Workplace POSH & Anti-Discrimination Guidelines",
    year: "Current",
    category: "Workplace",
    summary: "Guidelines under the Companies Act, SEBI BRSR mandate, and judicial precedents protecting queer professionals.",
    keyRights: [
      "Companies with >10 employees must have an Internal Complaints Committee (ICC).",
      "Protection against hostile work environments, deadnaming, and outing without consent.",
      "Equal opportunity policies must be explicitly published on corporate portals."
    ]
  }
];
