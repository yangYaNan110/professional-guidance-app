import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useNavigate, useParams } from 'react-router-dom';

// Fixed content for lines 935-955 (origin and development sections)
const fixedSection1 = `
                <div className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-xl p-6 border border-blue-100 dark:border-blue-800">
                  <h3 className="font-semibold text-blue-900 dark:text-blue-300 mb-4 flex items-center gap-2">
                    <span className="text-lg">🌱</span>起源与发展
                  </h3>
                  <div className="space-y-3">
                    {majorV2.major_concepts.origin?.map((item, idx) => (
                      <div key={idx} className="text-sm text-gray-700 dark:text-gray-300">
                        <div className="font-medium text-blue-700 dark:text-blue-400 mb-1">
                          {item.year && \`\${item.year年：\`}{item.title}
                        </div>
                        <p className="leading-relaxed">{item.content}</p>
                      </div>
                    ))}
                    {majorV2.major_concepts.development_history?.map((item, idx) => (
                      <div key={idx} className="text-sm text-gray-700 dark:text-gray-300">
                        <div className="font-medium text-blue-700 dark:text-blue-400 mb-1">
                          {item.year && \`\${item.year年：\`}{item.title}
                        </div>
                        <p className="leading-relaxed">{item.content}</p>
                      </div>
                    ))}
                  </div>
                </div>
`;

export default fixedSection1;