// Fix for the problematic section of MajorDetailPage.tsx

import { motion } from 'framer-motion'

// This is a temporary fix - replace the problematic section from line 940 to 1050

const fixedSection = `
          <div className="font-medium text-blue-700 dark:text-blue-400 mb-1">
            {item.year && \`\${item.year年：\`\}{item.title}
          </div>
          <p className="leading-relaxed">{item.content}</p>
`

export default fixedSection