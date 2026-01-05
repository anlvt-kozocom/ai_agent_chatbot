
import React from 'react';

const Features: React.FC = () => {
  const features = [
    {
      title: "Tra cứu siêu tốc",
      description: "Khách hàng chỉ cần nhập tên sản phẩm, Sigma sẽ hiển thị chi tiết thông tin, giá bán và tình trạng kho ngay lập tức.",
      icon: "⚡",
      color: "bg-amber-100 text-amber-600"
    },
    {
      title: "Chốt đơn tự động",
      description: "Tích hợp giỏ hàng và thanh toán ngay trong khung chat, giúp giảm 60% tỷ lệ bỏ rơi giỏ hàng của khách.",
      icon: "🛒",
      color: "bg-rose-100 text-rose-600"
    },
    {
      title: "Xử lý bảo hành AI",
      description: "Tự động phân loại yêu cầu bảo hành, hướng dẫn khách hàng gửi máy và theo dõi tiến độ sửa chữa 24/7.",
      icon: "🛡️",
      color: "bg-indigo-100 text-indigo-600"
    },
    {
      title: "Báo cáo thông minh",
      description: "Phân tích xu hướng hỏi đáp của khách hàng để giúp doanh nghiệp tối ưu tồn kho và chiến lược Marketing.",
      icon: "📊",
      color: "bg-green-100 text-green-600"
    }
  ];

  return (
    <div className="container mx-auto px-6">
      <div className="text-center max-w-3xl mx-auto mb-20">
        <h2 className="text-4xl md:text-5xl font-black text-slate-900 mb-6">Sức mạnh của Trợ lý Sigma</h2>
        <p className="text-slate-600 text-lg leading-relaxed">
          Được thiết kế để tối ưu trải nghiệm mua sắm hiện đại, Sigma không chỉ là một chat bot, mà là một nhân viên bán hàng xuất sắc nhất của bạn.
        </p>
      </div>
      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
        {features.map((feature, idx) => (
          <div key={idx} className="p-10 rounded-[32px] bg-white border border-slate-100 hover:shadow-2xl hover:shadow-rose-100 transition-all duration-500 hover:-translate-y-2 group">
            <div className={`w-16 h-16 rounded-2xl ${feature.color} flex items-center justify-center mb-8 text-3xl group-hover:scale-110 transition-transform shadow-inner`}>
              {feature.icon}
            </div>
            <h3 className="text-2xl font-bold text-slate-900 mb-4">{feature.title}</h3>
            <p className="text-slate-500 leading-relaxed font-medium">
              {feature.description}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Features;
