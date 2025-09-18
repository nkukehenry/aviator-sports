import { useState, useEffect } from 'react';
import Head from 'next/head';

// Types for the Python backend
interface Team {
  name: string;
  strength: number;
  attack: number;
  defense: number;
  form: number;
  home_advantage: number;
}

interface MatchEvent {
  id: string;
  type: string;
  team: string;
  minute: number;
  description: string;
  metadata?: any;
}

interface Match {
  id: string;
  home_team: Team;
  away_team: Team;
  home_score: number;
  away_score: number;
  current_minute: number;
  status: string;
  events: MatchEvent[];
  start_time?: string;
  end_time?: string;
  duration_minutes: number;
}

const API_BASE = 'http://localhost:5000/api';

export default function MVPDashboard() {
  const [matches, setMatches] = useState<Match[]>([]);
  const [liveMatches, setLiveMatches] = useState<Match[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedMatch, setSelectedMatch] = useState<Match | null>(null);

  useEffect(() => {
    fetchMatches();
    fetchLiveMatches();
    
    // Poll for updates every 2 seconds
    const interval = setInterval(() => {
      fetchLiveMatches();
      if (selectedMatch) {
        fetchMatch(selectedMatch.id);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [selectedMatch]);

  const fetchMatches = async () => {
    try {
      const response = await fetch(`${API_BASE}/matches`);
      const data = await response.json();
      if (data.success) {
        setMatches(data.data);
      }
    } catch (error) {
      console.error('Failed to fetch matches:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchLiveMatches = async () => {
    try {
      const response = await fetch(`${API_BASE}/matches/live`);
      const data = await response.json();
      if (data.success) {
        setLiveMatches(data.data);
      }
    } catch (error) {
      console.error('Failed to fetch live matches:', error);
    }
  };

  const fetchMatch = async (matchId: string) => {
    try {
      const response = await fetch(`${API_BASE}/matches/${matchId}`);
      const data = await response.json();
      if (data.success) {
        setSelectedMatch(data.data);
        // Update matches list
        setMatches(prev => prev.map(m => m.id === matchId ? data.data : m));
      }
    } catch (error) {
      console.error('Failed to fetch match:', error);
    }
  };

  const createSampleMatch = async () => {
    try {
      const response = await fetch(`${API_BASE}/matches/sample`, {
        method: 'POST',
      });
      const data = await response.json();
      if (data.success) {
        setMatches(prev => [...prev, data.data]);
      }
    } catch (error) {
      console.error('Failed to create sample match:', error);
    }
  };

  const startMatch = async (matchId: string) => {
    try {
      const response = await fetch(`${API_BASE}/matches/${matchId}/start`, {
        method: 'POST',
      });
      const data = await response.json();
      if (data.success) {
        setMatches(prev => prev.map(m => m.id === matchId ? data.data : m));
        if (selectedMatch?.id === matchId) {
          setSelectedMatch(data.data);
        }
      }
    } catch (error) {
      console.error('Failed to start match:', error);
    }
  };

  const stopMatch = async (matchId: string) => {
    try {
      const response = await fetch(`${API_BASE}/matches/${matchId}/stop`, {
        method: 'POST',
      });
      const data = await response.json();
      if (data.success) {
        setMatches(prev => prev.map(m => m.id === matchId ? data.data : m));
        if (selectedMatch?.id === matchId) {
          setSelectedMatch(data.data);
        }
      }
    } catch (error) {
      console.error('Failed to stop match:', error);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'live':
        return 'bg-red-100 text-red-800';
      case 'finished':
        return 'bg-gray-100 text-gray-800';
      case 'scheduled':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const formatTime = (minutes: number) => {
    const mins = Math.floor(minutes);
    const secs = Math.floor((minutes - mins) * 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading matches...</p>
        </div>
      </div>
    );
  }

  return (
    <>
      <Head>
        <title>VFL MVP - Live Match Simulation</title>
        <meta name="description" content="MVP Virtual Soccer Simulation" />
      </Head>

      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <div className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center py-6">
              <div>
                <h1 className="text-3xl font-bold text-gray-900">VFL MVP</h1>
                <p className="mt-1 text-sm text-gray-500">Virtual Soccer Match Simulation</p>
              </div>
              <div className="flex space-x-4">
                <button
                  onClick={createSampleMatch}
                  className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
                >
                  Create Sample Match
                </button>
                <div className="text-sm text-gray-500">
                  Live Matches: <span className="font-semibold text-red-600">{liveMatches.length}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Matches List */}
            <div className="lg:col-span-2">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">All Matches</h2>
              <div className="space-y-4">
                {matches.length === 0 ? (
                  <div className="text-center py-12 bg-white rounded-lg shadow">
                    <p className="text-gray-500">No matches yet. Create a sample match to get started!</p>
                  </div>
                ) : (
                  matches.map((match) => (
                    <div
                      key={match.id}
                      className={`bg-white rounded-lg shadow-sm border p-6 cursor-pointer transition-all ${
                        selectedMatch?.id === match.id ? 'ring-2 ring-blue-500' : 'hover:shadow-md'
                      }`}
                      onClick={() => setSelectedMatch(match)}
                    >
                      <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center space-x-3">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(match.status)}`}>
                            {match.status.toUpperCase()}
                          </span>
                          {match.status === 'live' && (
                            <span className="flex items-center text-red-600 text-sm">
                              <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse mr-1"></div>
                              LIVE
                            </span>
                          )}
                        </div>
                        <div className="text-sm text-gray-500">
                          {match.status === 'live' ? formatTime(match.current_minute) : '90:00'}
                        </div>
                      </div>

                      <div className="flex items-center justify-between">
                        <div className="text-center">
                          <div className="text-lg font-semibold text-gray-900">{match.home_team.name}</div>
                          <div className="text-sm text-gray-500">Strength: {match.home_team.strength}</div>
                        </div>
                        
                        <div className="text-center mx-8">
                          <div className="text-3xl font-bold text-blue-600">
                            {match.home_score} - {match.away_score}
                          </div>
                          <div className="text-xs text-gray-500">Score</div>
                        </div>
                        
                        <div className="text-center">
                          <div className="text-lg font-semibold text-gray-900">{match.away_team.name}</div>
                          <div className="text-sm text-gray-500">Strength: {match.away_team.strength}</div>
                        </div>
                      </div>

                      <div className="mt-4 flex justify-center space-x-2">
                        {match.status === 'scheduled' && (
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              startMatch(match.id);
                            }}
                            className="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700"
                          >
                            Start Match
                          </button>
                        )}
                        {match.status === 'live' && (
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              stopMatch(match.id);
                            }}
                            className="bg-red-600 text-white px-3 py-1 rounded text-sm hover:bg-red-700"
                          >
                            Stop Match
                          </button>
                        )}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Match Details */}
            <div className="lg:col-span-1">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Match Details</h2>
              {selectedMatch ? (
                <div className="bg-white rounded-lg shadow-sm border p-6">
                  <div className="mb-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(selectedMatch.status)}`}>
                        {selectedMatch.status.toUpperCase()}
                      </span>
                      {selectedMatch.status === 'live' && (
                        <span className="text-sm text-gray-500">
                          {formatTime(selectedMatch.current_minute)}
                        </span>
                      )}
                    </div>
                    
                    <div className="text-center mb-4">
                      <div className="text-2xl font-bold text-gray-900">
                        {selectedMatch.home_score} - {selectedMatch.away_score}
                      </div>
                    </div>

                    <div className="space-y-2 mb-6">
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">{selectedMatch.home_team.name}</span>
                        <span className="text-sm font-medium">Attack: {selectedMatch.home_team.attack} | Defense: {selectedMatch.home_team.defense}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">{selectedMatch.away_team.name}</span>
                        <span className="text-sm font-medium">Attack: {selectedMatch.away_team.attack} | Defense: {selectedMatch.away_team.defense}</span>
                      </div>
                    </div>
                  </div>

                  <div>
                    <h3 className="text-lg font-medium text-gray-900 mb-3">Match Events</h3>
                    <div className="space-y-2 max-h-64 overflow-y-auto">
                      {selectedMatch.events.length === 0 ? (
                        <p className="text-sm text-gray-500">No events yet</p>
                      ) : (
                        selectedMatch.events.map((event) => (
                          <div key={event.id} className="text-sm p-2 bg-gray-50 rounded">
                            <div className="flex justify-between">
                              <span className="font-medium">{event.minute}'</span>
                              <span className="text-gray-600">{event.description}</span>
                            </div>
                          </div>
                        ))
                      )}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="bg-white rounded-lg shadow-sm border p-6 text-center">
                  <p className="text-gray-500">Select a match to view details</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
