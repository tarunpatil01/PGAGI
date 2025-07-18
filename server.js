require('dotenv').config();
const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');

// MongoDB connection
const MONGODB_URL = process.env.MONGODB_URL || 'mongodb://localhost:27017/talentScout';
mongoose.connect(MONGODB_URL, { useNewUrlParser: true, useUnifiedTopology: true })
  .then(() => console.log('✅ MongoDB connected'))
  .catch(err => console.error('❌ MongoDB connection error:', err));

// Mongoose Schemas
const QuestionAnswerSchema = new mongoose.Schema({
  question: { type: String, required: true },
  answer: { type: String, required: true }
});

const UserSchema = new mongoose.Schema({
  fullName: { type: String, required: true },
  emailAddress: { type: String, required: true, unique: true },
  phoneNumber: { type: String, required: true },
  yearsOfExperience: { type: Number, required: true },
  desiredPositions: [{ type: String, required: true }],
  currentLocation: { type: String, required: true },
  techStack: [{ type: String, required: true }],
  questionsAndAnswers: [QuestionAnswerSchema],
  createdAt: { type: Date, default: Date.now }
});

const User = mongoose.model('User', UserSchema);

// Express app setup
const app = express();
app.use(cors());
app.use(express.json());

// Save user data
app.post('/api/user', async (req, res) => {
  try {
    const user = new User(req.body);
    await user.save();
    res.status(201).json({ message: 'User saved', user });
  } catch (err) {
    if (err.code === 11000) {
      res.status(409).json({ error: 'Email already exists' });
    } else {
      res.status(400).json({ error: err.message });
    }
  }
});

// Get user by email
app.get('/api/user/:email', async (req, res) => {
  try {
    const user = await User.findOne({ emailAddress: req.params.email });
    if (!user) return res.status(404).json({ error: 'User not found' });
    res.json(user);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

// Health check
app.get('/', (req, res) => {
  res.send('TalentScout backend is running.');
});

// Start server
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`🚀 Server running on port ${PORT}`);
});