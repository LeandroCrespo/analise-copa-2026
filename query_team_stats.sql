-- Query para buscar estatísticas dos times da Copa 2026
SELECT 
    t.name as team_name,
    COUNT(*) as total_games,
    AVG(CASE WHEN m.home_team_id = t.id THEN m.home_goals ELSE m.away_goals END) as avg_goals_scored,
    AVG(CASE WHEN m.home_team_id = t.id THEN m.away_goals ELSE m.home_goals END) as avg_goals_conceded
FROM teams t
JOIN matches m ON (m.home_team_id = t.id OR m.away_team_id = t.id)
WHERE t.name IN ('United States', 'Wales', 'Panama', 'Trinidad and Tobago', 'Mexico', 'Jamaica', 'Costa Rica', 'Honduras', 'Canada', 'Peru', 'Chile', 'Paraguay', 'Brazil', 'Colombia', 'Ecuador', 'Venezuela', 'Argentina', 'Uruguay', 'Bolivia', 'Haiti', 'England', 'Scotland', 'Republic of Ireland', 'Northern Ireland', 'Spain', 'Portugal', 'Morocco', 'Egypt', 'France', 'Netherlands', 'Belgium', 'Denmark', 'Germany', 'Italy', 'Switzerland', 'Austria', 'Croatia', 'Poland', 'Serbia', 'Ukraine', 'Japan', 'South Korea', 'Australia', 'Iran', 'Senegal', 'Nigeria', 'Cameroon', 'Ghana')
AND m.date >= '2020-01-01'
GROUP BY t.name
ORDER BY t.name
