from django.shortcuts import render
from django.views.generic import TemplateView


class HomeView(TemplateView):
    """
    Landing page view with all sections.
    """
    template_name = 'landing/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Pricing plans data
        context['pricing_plans'] = [
            {
                'name': 'Basic',
                'price': 29,
                'period': 'month',
                'description': 'Perfect for individual agents',
                'features': [
                    '50 descriptions per month',
                    'All property types',
                    'Multiple tone options',
                    'Email support',
                    'Copy & save descriptions',
                ],
                'cta_text': 'Start Basic',
                'recommended': False,
            },
            {
                'name': 'Pro',
                'price': 79,
                'period': 'month',
                'description': 'Great for small agencies',
                'features': [
                    '200 descriptions per month',
                    'All property types',
                    'Multiple tone options',
                    'Priority email support',
                    'Copy & save descriptions',
                    'Advanced customization',
                ],
                'cta_text': 'Start Pro',
                'recommended': True,
            },
            {
                'name': 'Agency',
                'price': 199,
                'period': 'month',
                'description': 'For large agencies and teams',
                'features': [
                    'Unlimited descriptions',
                    'All property types',
                    'Multiple tone options',
                    '24/7 priority support',
                    'Copy & save descriptions',
                    'Advanced customization',
                    'Team collaboration',
                    'API access',
                ],
                'cta_text': 'Start Agency',
                'recommended': False,
            },
        ]

        # Team members data
        context['team_members'] = [
            {
                'name': 'Sarah Johnson',
                'role': 'CEO & Co-Founder',
                'bio': 'Former real estate agent with 15 years of experience. Passionate about using AI to transform the industry.',
                'avatar': 'https://ui-avatars.com/api/?name=Sarah+Johnson&background=2563eb&color=fff&size=200',
            },
            {
                'name': 'Michael Chen',
                'role': 'CTO & Co-Founder',
                'bio': 'AI engineer and full-stack developer. Previously led tech teams at major PropTech companies.',
                'avatar': 'https://ui-avatars.com/api/?name=Michael+Chen&background=2563eb&color=fff&size=200',
            },
            {
                'name': 'Emily Rodriguez',
                'role': 'Head of Product',
                'bio': 'Product manager with a track record of building successful SaaS products. Focused on user experience.',
                'avatar': 'https://ui-avatars.com/api/?name=Emily+Rodriguez&background=2563eb&color=fff&size=200',
            },
            {
                'name': 'David Thompson',
                'role': 'Customer Success Lead',
                'bio': 'Dedicated to ensuring our customers get the most value from ListingCraft. Real estate background.',
                'avatar': 'https://ui-avatars.com/api/?name=David+Thompson&background=2563eb&color=fff&size=200',
            },
            {
                'name': 'Jessica Lee',
                'role': 'Marketing Director',
                'bio': 'Growth marketing expert helping real estate professionals discover the power of AI-generated content.',
                'avatar': 'https://ui-avatars.com/api/?name=Jessica+Lee&background=2563eb&color=fff&size=200',
            },
        ]

        # FAQ data
        context['faqs'] = [
            {
                'question': 'How does AI-generated content work?',
                'answer': 'Our AI uses advanced natural language processing to analyze your property details and generate compelling, SEO-optimized descriptions. The DeepSeek API powers our generation engine, ensuring high-quality, human-like text.',
            },
            {
                'question': 'Can I edit the generated descriptions?',
                'answer': 'Absolutely! All generated descriptions are fully editable. You can modify, save, and reuse them as needed. Think of it as a starting point that you can customize to match your style.',
            },
            {
                'question': 'What property types are supported?',
                'answer': 'We support all major property types including apartments, houses, villas, studios, commercial spaces, land, and more. Each type is optimized with specific keywords and phrasing.',
            },
            {
                'question': 'How many descriptions can I generate?',
                'answer': 'It depends on your plan. Basic allows 50/month, Pro allows 200/month, and Agency offers unlimited generations. You can upgrade or downgrade anytime.',
            },
            {
                'question': 'Is there a free trial?',
                'answer': 'Yes! All new users get a 14-day free trial with full access to Pro features. No credit card required to start.',
            },
            {
                'question': 'What languages are supported?',
                'answer': 'Currently, we support English with plans to add Spanish, French, and Arabic in the coming months. Let us know which languages you need!',
            },
            {
                'question': 'Can I cancel anytime?',
                'answer': 'Yes, you can cancel your subscription at any time. No long-term contracts or cancellation fees. Your access continues until the end of your billing period.',
            },
            {
                'question': 'Do you offer refunds?',
                'answer': 'We offer a 30-day money-back guarantee. If you\'re not satisfied within the first 30 days, we\'ll refund your payment, no questions asked.',
            },
        ]

        return context
