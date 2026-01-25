        {/* 📚 专业概念介绍 - 新的四个分组内容，按照要求必须放在最前面 */}
        {majorV2?.major_concepts && (
          <div className="mb-8">
            <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2 pb-2 border-b border-gray-100 dark:border-gray-700"><span>📚</span> 专业概念介绍</h2>
            
            <div className="space-y-6">
              {/* 起源与发展 */}
              {(majorV2.major_concepts.origin?.length > 0 || majorV2.major_concepts.development_history?.length > 0) && (
                <div className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-xl p-6 border border-blue-100 dark:border-blue-800">
                  <h3 className="font-semibold text-blue-900 dark:text-blue-300 mb-4 flex items-center gap-2">
                    <span className="text-lg">🌱</span>起源与发展
                  </h3>
                  <div className="space-y-3">
                    {majorV2.major_concepts.origin?.map((item, idx) => (
                      <div key={idx} className="text-sm text-gray-700 dark:text-gray-300">
                        <div className="font-medium text-blue-700 dark:text-blue-400 mb-1">
                          {item.year && `${item.year年：`}{item.title}
                        </div>
                        <p className="leading-relaxed">{item.content}</p>
                      </div>
                    ))}
                    {majorV2.major_concepts.development_history?.map((item, idx) => (
                      <div key={idx} className="text-sm text-gray-700 dark:text-gray-300">
                        <div className="font-medium text-blue-700 dark:text-blue-400 mb-1">
                          {item.year && `${item.year年：`}{item.title}
                        </div>
                        <p className="leading-relaxed">{item.content}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* 重大事件 */}
              {majorV2.major_concepts.major_events?.length > 0 && (
                <div className="bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 rounded-xl p-6 border border-purple-100 dark:border-purple-800">
                  <h3 className="font-semibold text-purple-900 dark:text-purple-300 mb-4 flex items-center gap-2">
                    <span className="text-lg">⚡</span>重大事件
                  </h3>
                  <div className="space-y-3">
                    {majorV2.major_concepts.major_events.map((item, idx) => (
                      <div key={idx} className="text-sm text-gray-700 dark:text-gray-300">
                        <div className="font-medium text-purple-700 dark:text-purple-400 mb-1">
                          {item.year && `${item.year年：`}{item.title}
                        </div>
                        <p className="leading-relaxed">{item.content}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* 现状与爆发 */}
              {majorV2.major_concepts.current_status?.length > 0 && (
                <div className="bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 rounded-xl p-6 border border-green-100 dark:border-green-800">
                  <h3 className="font-semibold text-green-900 dark:text-green-300 mb-4 flex items-center gap-2">
                    <span className="text-lg">🚀</span>现状与爆发
                  </h3>
                  <div className="space-y-3">
                    {majorV2.major_concepts.current_status.map((item, idx) => (
                      <div key={idx} className="text-sm text-gray-700 dark:text-gray-300">
                        <div className="font-medium text-green-700 dark:text-green-400 mb-1">
                          {item.year && `${item.year年：`}{item.title}
                        </div>
                        <p className="leading-relaxed">{item.content}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* 未来展望 */}
              {majorV2.major_concepts.future_prospects?.length > 0 && (
                <div className="bg-gradient-to-r from-orange-50 to-amber-50 dark:from-orange-900/20 dark:to-amber-900/20 rounded-xl p-6 border border-orange-100 dark:border-orange-800">
                  <h3 className="font-semibold text-orange-900 dark:text-orange-300 mb-4 flex items-center gap-2">
                    <span className="text-lg">🔮</span>未来展望
                  </h3>
                  <div className="space-y-3">
                    {majorV2.major_concepts.future_prospects.map((item, idx) => (
                      <div key={idx} className="text-sm text-gray-700 dark:text-gray-300">
                        <div className="font-medium text-orange-700 dark:text-orange-400 mb-1">
                          {item.year && `${item.year年：`}{item.title}
                        </div>
                        <p className="leading-relaxed">{item.content}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* 兜底显示：如果新API没有数据，显示旧的专业介绍 */}
        {!majorV2?.major_concepts && (
          <div className="mb-8">
            <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2 pb-2 border-b border-gray-100 dark:border-gray-700"><span>💡</span> 专业介绍</h2>
            <div className="space-y-4">
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white mb-2">专业概念</h3>
                <p className="text-gray-700 dark:text-gray-300 leading-relaxed">{major.description}</p>
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white mb-2">培养目标</h3>
                <p className="text-gray-700 dark:text-gray-300 leading-relaxed">{major.training_objective}</p>
              </div>
            </div>
          </div>
        )}